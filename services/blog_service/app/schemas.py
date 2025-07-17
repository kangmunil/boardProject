from typing import Optional, List
from sqlmodel import SQLModel
from datetime import datetime

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
