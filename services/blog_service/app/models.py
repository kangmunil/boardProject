from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import BaseModel
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

class ArticleImage(SQLModel, table=True):
    id: Optional[int] = Field(default = None, primary_key=True)
    image_filename: str
    article_id: Optional[int]=Field(default=None, index=True)

class BlogArticle(SQLModel, table=True):
    id: Optional[int]=Field(default=None, primary_key=True)
    title: str=Field(index=True)
    content: str
    create_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/seoul")))
    owner_id: int
    tags: Optional[str] = Field(default=None)

class BlogPostCreate(SQLModel):
    title: str
    content: str
    tags: Optional[str] = None

class BlogPostPublic(SQLModel):
    id: int
    title: str
    content: str
    create_at: datetime
    owner_id: int
    tags: Optional[str] = None
