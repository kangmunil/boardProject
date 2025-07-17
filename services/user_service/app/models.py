from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, String, Integer

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str = Field(sa_column=Column(String, unique=True, index=True))
    name: str
    hashed_password: str
    bio: Optional[str]
    profile_image_url:Optional[str] = None
    birthday: str
    gender: Optional[str] = None
    phone: str = Field(sa_column=Column(String, unique=True, index=True))