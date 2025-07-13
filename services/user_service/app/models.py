from typing import Optional
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str = Field(unique=True, index=True) # 이메일 필드 추가
    hashed_password: str
    bio: Optional[str]
    profile_image_frame:Optional[str] = None

class UserCreate(SQLModel):
    username: str
    email: str
    password: str
    name: str
    birthday: str
    gender: Optional[str] = None
    phone: str
    bio: Optional[str] = None

class Userlogin(SQLModel):
    email: str
    password: str

class UserPublic(SQLModel):
    id: int
    username: str
    email: str
    bio: Optional[str] = None
    profile_image_url: Optional[str]