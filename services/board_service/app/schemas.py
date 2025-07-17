from typing import Optional, List
from sqlmodel import SQLModel, Field
from datetime import datetime

class PostCreate(SQLModel):
    title: str
    content: str
    is_notice: bool = False

class PostUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_notice: Optional[bool] = None

class PostList(SQLModel):
    id: int
    title: str
    created_at: datetime
    views: int

class PostRead(PostList):
    content: str
    owner_id: int