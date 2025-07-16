from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel
from datetime import datetime
from zoneinfo import ZoneInfo

class ArticleImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    image_filename: str
    article_id: Optional[int] = Field(default=None, foreign_key="blogarticle.id")

    article: "BlogArticle" = Relationship(back_populates="images")

class BlogArticle(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    content: str
    create_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Seoul")))
    owner_id: int
    tags: Optional[str] = Field(default=None)

    images: List["ArticleImage"] = Relationship(back_populates="article")

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
    images: List[str] = [] # 이미지 파일명 리스트 추가
