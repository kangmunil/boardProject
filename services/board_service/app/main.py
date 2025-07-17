import os
import httpx
import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, status, Header, Query, status, Response
from typing import Annotated, Optional, List
from sqlmodel import select, Relationship
from sqlmodel.ext.asyncio.session import AsyncSession

from database import init_db, get_session
from redis_client import get_redis
from models import Post
from schemas import PostCreate, PostRead
from sqlalchemy.orm import Session
from sqlalchemy import update


app = FastAPI(title="Board Service")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")

STATIC_DIR = "/app/static"
IMAGE_DIR = f"{STATIC_DIR}/images"
os.makedirs(IMAGE_DIR, exist_ok=True)

@app.get("/")
def health_check():
    return {"status": "Board service running"}

@app.post("/board", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    session: AsyncSession = Depends(get_session),
):
    db_post = Post.model_validate(post)
    session.add(db_post)
    await session.commit()
    await session.refresh(db_post)
    return db_post

@app.get("/board", response_model=list[Post])
def list_posts(
    offset: int = 0,
    limit: int = 20,
    session: Session = Depends(get_session),
):
    stmt = (
        select(Post)
        .where(Post.is_published == True)
        .order_by(Post.is_notice.desc(), Post.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return session.exec(stmt).all()

app.get("/board/{post_id}", response_model=PostRead)
def read_post(
    post_id: int,
    inc_view: bool = True,
    session: Session = Depends(get_session),
):
    post = session.get(Post, post_id)
    if not post or not post.is_published:
        raise HTTPException(status_code=404, detail="post not found")

    if inc_view:
        session.exec(
            update(Post).where(Post.id == post_id).values(views=Post.views + 1)
        )
        session.commit()
        session.refresh(post)

    return post