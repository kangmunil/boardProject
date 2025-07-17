from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, func, Boolean

class Post(SQLModel, table=True):
    __tablename__ = "posts"
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(
        sa_column=Column(String(200), nullable=False, index=True)
    )
    content: str = Field(
        sa_column=Column(Text, nullable=False)
    )
    is_published: bool = Field(default=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True),
                         server_default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True),
                         onupdate=func.now(),
                         server_default=func.now(),
                         nullable=False)
    )
    views: int = Field(
        default=0,
        sa_column=Column(Integer, nullable=False, server_default="0")
    )
    owner_id: int = Field(foreign_key="users.id")
    is_notice: bool = Field(default=False, sa_column=Column(Boolean, nullable=False, server_default="0"))  