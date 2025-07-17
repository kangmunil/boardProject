from typing import Optional
from sqlmodel import SQLModel
from pydantic import BaseModel

class UserList(BaseModel):
    id: int
    username: str
    email: str
    bio: Optional[str] = None

    class Config:
        orm_mode = True

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

class UserLogin(SQLModel):
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
