from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import BaseModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str = Field(unique=True, index=True)
    name: str
    hashed_password: str
    bio: Optional[str]
    profile_image_url:Optional[str] = None
    birthday: str
    gender: Optional[str] = None
    phone: str = Field(unique=True, index=True)

class UserCreate(SQLModel):
    username: str
    email: str
    password: str
    name: str
    birthday: str
    gender: Optional[str] = None
    phone: str
    bio: Optional[str] = None

class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    birthday: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None

class Userlogin(SQLModel):
    email: str
    password: str

class UserPublic(SQLModel):
    id: int
    username: str
    email: str
    name: str
    birthday: str
    gender: Optional[str] = None
    phone: str
    bio: Optional[str] = None
    profile_image_url: Optional[str]

class UpdatePassword(SQLModel):
    current_password: str
    new_password: str