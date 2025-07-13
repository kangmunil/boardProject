import os
import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware # CORS 미들웨어 임포트

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
    print(path)
    print(USER_SERVICE_URL)
    if path.startswith("/api/users") or path.startswith("/api/auth"):
        base_url = USER_SERVICE_URL
    elif path.startswith("/api/board"):
        base_url = BOARD_SERVICE_URL
    elif path.startswith("/api/blog"):
        base_url = BLOG_SERVICE_URL
    else:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    url = f"{base_url}{path}?{request.url.query}"
    
    try:
        rp_resp = await client.request(
            method=request.method,
            url=url,
            headers=request.headers.raw,
            content=await request.body()
        )
        
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