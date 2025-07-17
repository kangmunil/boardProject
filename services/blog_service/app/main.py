import os
import httpx
from fastapi import FastAPI, Depends, HTTPException, status, Header, Form, File, UploadFile
from typing import Annotated, Optional, List
from sqlmodel import select, Relationship
from sqlmodel.ext.asyncio.session import AsyncSession
from database import init_db, get_session
from models import BlogArticle, ArticleImage
from schemas import BlogPostCreate, BlogPostPublic
import math
from datetime import datetime
from zoneinfo import ZoneInfo
import uuid
import aiofiles
from starlette.staticfiles import StaticFiles
from sqlalchemy.orm import selectinload
from sqlalchemy import func

app = FastAPI(title="Blog Service")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")

STATIC_DIR = "/app/static"
IMAGE_DIR = f"{STATIC_DIR}/images"
os.makedirs(IMAGE_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.on_event("startup")
async def on_startup():
    await init_db()

async def get_current_user_id(
    x_user_id: Annotated[int | None, Header(alias="X-User-Id")] = None
) -> int:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated: X-User-Id header missing")
    return x_user_id

@app.get("/")
def health_check():
    return {"status": "Blog service running"}

@app.post("/blog/posts", response_model=BlogPostPublic, status_code=status.HTTP_201_CREATED)
async def create_blog_post(
    session: Annotated[AsyncSession, Depends(get_session)],
    owner_id: Annotated[int, Depends(get_current_user_id)],
    title: str = Form(...),
    content: str = Form(...),
    tags: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    async with session.begin(): # Add transaction block
        db_post = BlogArticle(
            title=title,
            content=content,
            tags=tags,
            owner_id=owner_id,
            create_at=datetime.now(ZoneInfo("Asia/Seoul"))
        )
        session.add(db_post)
        await session.flush() # Flush to make db_post.id available

        loaded_images = [] # Initialize loaded_images here

        if file:
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(IMAGE_DIR, unique_filename)
            try:
                async with aiofiles.open(file_path, 'wb') as out_file:
                    while content_chunk := await file.read(1024):
                        await out_file.write(content_chunk)
                
                article_image = ArticleImage(
                    image_filename=unique_filename,
                    article_id=db_post.id
                )
                session.add(article_image)
                
                loaded_images = [article_image.image_filename]

            except Exception as e:
                print(f"[ERROR] Failed to save image: {e}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"이미지 저장 실패: {e}")

        

        return BlogPostPublic(
            id=db_post.id,
            title=db_post.title,
            content=db_post.content,
            create_at=db_post.create_at,
            owner_id=db_post.owner_id,
            tags=db_post.tags,
            images=loaded_images
        )

@app.get("/blog/posts", response_model=List[BlogPostPublic])
async def get_blog_posts(
    session: Annotated[AsyncSession, Depends(get_session)],
    page: int = 1,
    size: int = 20
):
    offset = (page - 1) * size
    
    # 총 게시물 수 조회
    total_posts = await session.scalar(select(func.count(BlogArticle.id)))
    
    # 페이징 처리된 게시물 조회
    statement = select(BlogArticle).options(selectinload(BlogArticle.images)).offset(offset).limit(size).order_by(BlogArticle.create_at.desc())
    posts = await session.exec(statement)
    
    return [
        BlogPostPublic(
            id=post.id,
            title=post.title,
            content=post.content,
            create_at=post.create_at,
            owner_id=post.owner_id,
            tags=post.tags,
            images=[img.image_filename for img in list(post.images)]
        )
        for post in posts.all()
    ]

@app.get("/blog/posts/{post_id}", response_model=BlogPostPublic)
async def get_blog_post(
    post_id: int,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    statement = select(BlogArticle).options(selectinload(BlogArticle.images)).where(BlogArticle.id == post_id)
    result = await session.exec(statement)
    post = result.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    return BlogPostPublic(
        id=post.id,
        title=post.title,
        content=post.content,
        create_at=post.create_at,
        owner_id=post.owner_id,
        tags=post.tags,
        images=[img.image_filename for img in post.images]
    )