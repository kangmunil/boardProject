import os
import httpx
from fastapi import FastAPI, Depends, HTTPException, status, Header
from typing import Annotated, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from database import init_db, get_session
from models import BlogArticle, BlogPostCreate, BlogPostPublic
import math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

app = FastAPI(title="Blog Service")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")

@app.on_event("startup")
async def on_startup():
    await init_db()

async def get_current_user_id(
    x_user_id: Annotated[int | None, Header(alias="X-User-Id")] = None
) -> int:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated: X-User-Id header missing")
    
    # user_service에 사용자 ID 유효성 검사 요청 (선택 사항, 필요시 활성화)
    # try:
    #     async with httpx.AsyncClient() as client:
    #         response = await client.get(f"{USER_SERVICE_URL}/api/users/{x_user_id}")
    #         response.raise_for_status()
    # except httpx.HTTPStatusError as e:
    #     if e.response.status_code == 404:
    #         raise HTTPException(status_code=401, detail="Not authenticated: User not found")
    #     raise HTTPException(status_code=500, detail=f"User service error: {e}")
    # except httpx.RequestError as e:
    #     raise HTTPException(status_code=500, detail=f"Could not connect to user service: {e}")

    return x_user_id

@app.get("/")
def health_check():
    return {"status": "Blog service running"}

@app.post("/api/blog/posts", response_model=BlogPostPublic, status_code=status.HTTP_201_CREATED)
async def create_blog_post(
    post: BlogPostCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    owner_id: Annotated[int, Depends(get_current_user_id)]
):
    db_post = BlogArticle(
        title=post.title,
        content=post.content,
        tags=post.tags,
        owner_id=owner_id,
        create_at=datetime.now(ZoneInfo("Asia/Seoul"))
    )
    session.add(db_post)
    await session.commit()
    await session.refresh(db_post)
    return db_post

@app.get("/api/blog/posts", response_model=list[BlogPostPublic])
async def get_blog_posts(
    session: Annotated[AsyncSession, Depends(get_session)],
    page: int = 1,
    size: int = 20
):
    offset = (page - 1) * size
    
    # 총 게시물 수 조회
    total_posts_statement = select(BlogArticle)
    total_posts_result = await session.exec(total_posts_statement)
    total_posts = len(total_posts_result.all())
    
    # 페이징 처리된 게시물 조회
    statement = select(BlogArticle).offset(offset).limit(size).order_by(BlogArticle.create_at.desc())
    posts = await session.exec(statement)
    
    return posts.all()

@app.get("/api/blog/posts/{post_id}", response_model=BlogPostPublic)
async def get_blog_post(
    post_id: int,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    post = await session.get(BlogArticle, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post