import os
import httpx
from fastapi import FastAPI, Request, Response, HTTPException, status, UploadFile
from fastapi.middleware.cors import CORSMiddleware # CORS 미들웨어 임포트
import urllib.parse # 추가

app = FastAPI(title="API Gateway")

# ▼▼▼ CORS 미들웨어 추가 ▼▼▼
origins = [
    "http://localhost",
    "http://127.0.0.1",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # 쿠키를 포함한 요청을 허용하려면 반드시 True
    allow_methods=["*"],     # 모든 HTTP 메서드 허용
    allow_headers=["*"],     # 모든 HTTP 헤더 허용
)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
BOARD_SERVICE_URL = os.getenv("BOARD_SERVICE_URL")
BLOG_SERVICE_URL = os.getenv("BLOG_SERVICE_URL")

@app.on_event("startup")
async def startup_event():
    timeout = httpx.Timeout(10.0, connect=5.0)
    app.state.client = httpx.AsyncClient(timeout=timeout)

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.client.aclose()


@app.get("/api/users") # /api/users 요청을 처리
@app.get("/api/users/list") # /api/users/list 요청도 처리
async def get_users_from_user_service(request: Request):
    """
    /api/users 요청을 user_service의 /user/list로 전달합니다.
    """
    try:
        # user_service의 /user/list 엔드포인트로 요청을 보냅니다.
        response = await app.state.client.get(f"{USER_SERVICE_URL}/user/list", params=request.query_params)
        response.raise_for_status() # 200번대 응답이 아니면 예외 발생

        response_headers = dict(response.headers)
        response_headers.pop("content-length", None)
        response_headers.pop("content-encoding", None)

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers,
        )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"An error occurred while proxying to user_service: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"User service returned an error: {e.response.text}")

# ▼▼▼ 이 데코레이터에 methods를 추가하여 모든 요청 방식을 허용하도록 변경합니다. ▼▼▼
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def reverse_proxy(request: Request):
    path = request.url.path
    client: httpx.AsyncClient = request.app.state.client
    print(f"[DEBUG] Incoming request to gateway: {request.method} {path}")

    # 요청 헤더를 복사하여 수정할 수 있도록 합니다.
    headers = dict(request.headers)
    auth_headers = {}

    # 세션 ID 쿠키 확인 및 user_service를 통한 인증
    session_id = request.cookies.get("session_id")
    
    # 로그인 및 회원가입 요청은 인증 로직을 건너뜁니다.
    if not (path == "/api/auth/login" or path == "/api/auth/register"):
        if session_id:
            try:
                # user_service의 /api/auth/me 엔드포인트로 요청을 보냅니다.
                # 이때, 원래 요청의 session_id 쿠키를 전달합니다.
                auth_response = await client.get(
                    f"{USER_SERVICE_URL}/api/auth/me",
                    headers={"Cookie": f"session_id={session_id}"}
                )
                auth_response.raise_for_status() # 200번대 응답이 아니면 예외 발생
                user_data = auth_response.json()
                user_id = user_data.get("id")
                if user_id:
                    auth_headers["X-User-ID"] = str(user_id)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == status.HTTP_401_UNAUTHORIZED:
                    # GET /api/blog/posts 요청이 아니면 401을 반환
                    if not (request.method == "GET" and path == "/api/blog/posts"):
                        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
                    # GET /api/blog/posts 요청이면 인증 헤더 없이 진행
                else:
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"User service error: {e.response.text}")
            except httpx.RequestError as e:
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Could not connect to user service: {e}")

    # 블로그 게시물 생성 요청에 대한 인증 처리 (X-User-ID 헤더 추가)
    if request.method == "POST" and path == "/api/blog/posts":
        if "X-User-ID" not in auth_headers:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated for blog post creation")
        headers.update(auth_headers)
    elif auth_headers: # 다른 요청에도 인증 헤더가 있다면 추가
        headers.update(auth_headers)

    if path.startswith("/api/users") or path.startswith("/api/auth"):
        base_url = USER_SERVICE_URL
    elif path.startswith("/api/board"):
        base_url = BOARD_SERVICE_URL
    elif path.startswith("/api/blog"):
        base_url = BLOG_SERVICE_URL
    else:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    url = f"{base_url}{path}?{request.url.query}"
    
    # httpx 요청 파라미터 초기화
    httpx_params = {
        "method": request.method,
        "url": url,
        "headers": headers,
    }

    # POST, PUT, PATCH 요청에 대해 바디 처리
    if request.method in ["POST", "PUT", "PATCH"]:
        original_content_type = request.headers.get("content-type", "")
        print(f"[DEBUG] Original Content-Type: {original_content_type}")

        if "multipart/form-data" in original_content_type:
            print("[DEBUG] Proxying raw multipart/form-data request body to", url)
            body = await request.body()
            httpx_params["content"] = body
            headers["content-type"] = original_content_type
            httpx_params["headers"] = headers
        elif "application/x-www-form-urlencoded" in original_content_type:
            print(f"[DEBUG] Proxying x-www-form-urlencoded request to {base_url}{path}")
            try:
                # request.form()을 사용하여 파싱
                form_data = await request.form()
                data = {key: value for key, value in form_data.items()}
                httpx_params["data"] = data
                if "content-type" in httpx_params["headers"]:
                    del httpx_params["headers"]["content-type"]
            except Exception as e:
                print(f"[ERROR] Failed to parse x-www-form-urlencoded body: {e}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid form data")
        elif "application/json" in original_content_type:
            print(f"[DEBUG] Proxying application/json request to {base_url}{path}")
            httpx_params["json"] = await request.json()
        else:
            print(f"[DEBUG] Proxying request with unknown content-type: {original_content_type} to {base_url}{path}")
            # request.body()는 마지막에 호출
            httpx_params["content"] = await request.body()

    print(f"[DEBUG] httpx_params: {httpx_params}")
    try:
        rp_resp = await client.request(**httpx_params)
        print(f"[DEBUG] Received response from {base_url}{path}: {rp_resp.status_code}")
        
        response_headers = dict(rp_resp.headers)
        response_headers.pop("content-length", None)
        response_headers.pop("content-encoding", None)
        
        return Response(
            content=rp_resp.content,
            status_code=rp_resp.status_code,
            headers=response_headers,
        )
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {base_url}")
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail=f"Request timeout: {base_url}")