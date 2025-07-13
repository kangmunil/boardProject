from fastapi import FastAPI, status, Response, Depends, HTTPException, Form, Cookie
from typing import Annotated, Optional
from starlette.staticfiles import StaticFiles
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from redis_client import get_redis
from redis.asyncio import Redis
from schemas import UserList  # pydantic 모델: 공개해도 되는 필드만
import os
import math
#operating system

from models import User, UserCreate, UserPublic, Userlogin
from database import init_db, get_session
from auth import get_password_hash, create_session, verify_password, get_user_id_from_session, delete_session

app=FastAPI(title="User Service")

STATIC_DIR= "/app/static"
PROFILE_IMAGE_DIR = f"{STATIC_DIR}/profiles"
os.makedirs(PROFILE_IMAGE_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def create_user_public(user: User) -> UserPublic:
    image_url = f"/static/profiles/{user.profile_image_frame}" if user.profile_image_frame else "https://www.w3schoool.com/w3images/avater_g.jpg"
    user_dict = user.model_dump()
    user_dict["profile_image_filename"] = user.profile_image_frame
    user_dict["profile_image_url"] = image_url
    return UserPublic.model_validate(user_dict)

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/")
def health_check():
    return {"status":"User service runnng"}

@app.post('/api/auth/register', response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(
    response: Response,
    user_data: UserCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)]
):
    statement = select(User).where(User.email==user_data.email)
    exist_user_result = await session.exec(statement)

    if exist_user_result.one_or_none(): # one_or_none = 있어도되고 없어도 된다.
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 사용중인 이메일입니다. ")
    
    hashed_password = get_password_hash(user_data.password)
    new_user = User.model_validate(user_data, update={"hashed_password": hashed_password})

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user) # refresh된 데이터는 id값이 생성되서 돌아온다.

    session_id = await create_session(redis, new_user.id)
    response.set_cookie(key="session_id", value=session_id, httponly=True, samesite="lax", max_age=3600, path="/")

    return create_user_public(new_user)

@app.post("/api/auth/login", status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    email: str = Form(...),
    password: str = Form(...),
):
    statement = select(User).where(User.email == email)
    user_result = await session.exec(statement)
    user = user_result.one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다.",
        )

    session_id = await create_session(redis, user.id)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=3600,
        path="/",
    )
    return {"message": "로그인 성공"}

@app.get("/api/auth/me", response_model=UserPublic)
async def get_current_user(
    response: Response,
    redis: Annotated[Redis, Depends(get_redis)],
    session: Annotated[AsyncSession, Depends(get_session)],
    session_id: Annotated[Optional[str], Cookie()] = None
):
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    user_id = await get_user_id_from_session(redis, session_id)

    # 쿠키의 세션이 사라지게 한다
    if not user_id:
        response.delete_cookie("session_id", path="/")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found session")
    
    user = await session.get(User, int(user_id))
    
    if not user:
        response.delete_cookie("session_id", path="/")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return create_user_public(user)

@app.post("/api/auth/logout")
async def logout(
    response: Response,
    redis: Annotated[Redis, Depends(get_redis)],
    session_id: Annotated[Optional[str], Cookie()] = None
):
    if session_id:
        await delete_session(redis, session_id)
    response.delete_cookie("session_id", path="/")
    return {"message":"LOGOUT 성공"}

@app.get("/api/users", response_model=list[UserPublic])
async def get_all_users(session: Annotated[AsyncSession, Depends(get_session)]):
    statement = select(User)
    users = await session.exec(statement)
    return [create_user_public(user) for user in users.all()]

@app.get("/api/users/{user_id}", response_model=UserPublic)
async def get_user_by_id(
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_session)]
):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return create_user_public(user)

@app.get("/user/list", response_model=list[UserList])
async def get_user_list(session: Annotated[AsyncSession, Depends(get_session)]):
    result = await session.execute(select(User).order_by(User.id))
    users = result.scalars().all()
    return [UserList(id=user.id, username=user.username, email=user.email) for user in users]