from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import Column, String, Integer

class ArticleImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    image_filename: str
    article_id: Optional[int] = Field(default=None, foreign_key="blogarticle.id")

    article: "BlogArticle" = Relationship(back_populates="images")

class BlogArticle(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(sa_column=Column(String, index=True))
    content: str
    create_at: datetime = Field(default_factory=lambda: datetime.now(ZoneInfo("Asia/Seoul")))
    owner_id: int = Field(sa_column=Column(Integer, index=True))
    tags: Optional[str] = Field(default=None)

    images: List["ArticleImage"] = Relationship(back_populates="article")
