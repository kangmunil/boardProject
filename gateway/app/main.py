import httpx
import os
from fastapi import FastAPI, Request, Response

app = FastAPI(title="API Gateway")

# docker-compose.yml에서 설정한 환경 변수를 읽어옵니다.
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8000")

# HTTP 요청을 보내기 위한 비동기 클라이언트를 생성합니다.
# 앱이 실행되는 동안 연결을 재사용하여 효율성을 높입니다.
client = httpx.AsyncClient(base_url=USER_SERVICE_URL)

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def route_to_user_service(request: Request, path: str):
    """
    모든 /api/* 요청을 받아서 user_service로 전달하는 프록시 엔드포인트입니다.
    """
    # 1. user_service로 보낼 URL을 조합합니다.
    # client의 base_url이 설정되어 있으므로 경로만 전달하면 됩니다.
    url = f"/{path}"

    # 2. 원본 요청에서 헤더와 본문을 그대로 가져옵니다.
    headers = dict(request.headers)
    # 호스트 헤더는 실제 목적지로 변경해주는 것이 좋습니다.
    headers["host"] = client.base_url.host
    
    req_body = await request.body()

    # 3. httpx를 사용해 user_service로 요청을 전달합니다.
    try:
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=req_body,
            params=request.query_params,
            timeout=30.0, # 타임아웃 설정
        )
    except httpx.RequestError as e:
        # user_service에 연결할 수 없는 경우 에러를 반환합니다.
        return Response(content=f"An error occurred while proxying to user_service: {e}", status_code=503)


    # 4. user_service로부터 받은 응답을 클라이언트에게 그대로 반환합니다.
    # 헤더 중 일부는 프록시 환경에서 불필요하므로 제외할 수 있습니다.
    response_headers = dict(response.headers)
    response_headers.pop("content-encoding", None)
    response_headers.pop("transfer-encoding", None)

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=response_headers,
    )