from fastapi import FastAPI, status, Response, Depends, HTTPException, Form, Cookie, UploadFile, File, Header, Request
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
import uuid
import aiofiles
#operating system

from models import User
from schemas import UserCreate, UserPublic, UserLogin, UserUpdate, UpdatePassword
from database import init_db, get_session
from auth import get_password_hash, create_session, verify_password, get_user_id_from_session, delete_session

app=FastAPI(title="User Service")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"[DEBUG] Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"[DEBUG] Outgoing response: {response.status_code}")
    return response

STATIC_DIR= "/app/static"
PROFILE_IMAGE_DIR = f"{STATIC_DIR}/profiles"
os.makedirs(PROFILE_IMAGE_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def create_user_public(user: User) -> UserPublic:
    image_url = user.profile_image_url if user.profile_image_url else "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ-JdoMKl_cBoE-qqWZjn7OH-dvmZK73uVZ9w&s"
    user_dict = user.model_dump()
    user_dict["profile_image_url"] = image_url
    return UserPublic.model_validate(user_dict)

async def get_current_user_id(
        session_id: Annotated[str | None, Cookie()] = None,
        redis: Annotated[Redis, Depends(get_redis)] = None
) -> int:
    if not session_id:
        raise HTTPException(status_code=401, detail="Not Authenticated")
    user_id_str = await get_user_id_from_session(redis, session_id)
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Invalid session")
    return int(user_id_str)

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/")
def health_check():
    return {"status":"User service runnng"}

@app.post("/test-post")
async def test_post_endpoint(request: Request):
    body = await request.body()
    print(f"[DEBUG] Test POST endpoint received body: {body.decode()}")
    return {"message": "Test POST successful"}

from starlette.requests import Request, ClientDisconnect

@app.post('/auth/register', response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    request: Request # Request 객체로 변경
):
    try:
        form_data = await request.form() # 폼 데이터 직접 파싱
    except ClientDisconnect:
        return {"error": "Client disconnected before the request was completed."}
    username = form_data.get("username")
    email = form_data.get("email")
    password = form_data.get("password")
    name = form_data.get("name")
    birthday = form_data.get("birthday")
    gender = form_data.get("gender")
    phone = form_data.get("phone")
    bio = form_data.get("bio")
    file = form_data.get("profile_image") # 파일은 UploadFile 객체로 가져옴
    print(f"[DEBUG] Received profile_image: {file}, type: {type(file)}")

    if not all([username, email, password, name, birthday, phone]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="필수 정보를 모두 입력해주세요.")

    print(f"[DEBUG] Register attempt for email: {email}")
    statement = select(User).where(User.email==email)
    exist_user_result = await session.exec(statement)

    if exist_user_result.one_or_none():
        print(f"[DEBUG] Email already exists: {email}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 사용중인 이메일입니다. ")
    
    hashed_password = get_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        name=name,
        birthday=birthday,
        gender=gender,
        phone=phone,
        bio=bio,
        profile_image_url=None # 초기값으로 None 설정
    )

    if file:
        print(f"[DEBUG] Registering user with image: {file.filename}, size: {file.size}")
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(PROFILE_IMAGE_DIR, unique_filename)
        try:
            async with aiofiles.open(file_path, 'wb') as out_file:
                while content := await file.read(1024):
                    await out_file.write(content)
            new_user.profile_image_url = f"/static/profile_images/{unique_filename}"
            print(f"[DEBUG] Image saved to: {file_path}")
            print(f"[DEBUG] New user profile_image_url set to: {new_user.profile_image_url}")
        except Exception as e:
            print(f"[ERROR] Failed to save image during registration: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"이미지 저장 실패: {e}")

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    session_id = await create_session(redis, new_user.id)
    response.set_cookie(key="session_id", value=session_id, httponly=True, samesite="lax", max_age=3600, path="/")
    print(f"[DEBUG] Registration successful for email: {email}, session_id: {session_id}")
    # 세션 생성 후 바로 get_user_id_from_session 호출하여 확인
    retrieved_user_id = await get_user_id_from_session(redis, session_id)
    print(f"[DEBUG] After registration, retrieved user_id from session: {retrieved_user_id}")
    return create_user_public(new_user)

@app.post("/auth/login", status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    request: Request # Request 객체로 변경
):
    form_data = await request.form() # 폼 데이터 직접 파싱
    email = form_data.get("email")
    password = form_data.get("password")

    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이메일과 비밀번호를 입력해주세요.")

    print(f"[DEBUG] Login attempt for email: {email}")
    statement = select(User).where(User.email == email)
    user_result = await session.exec(statement)
    user = user_result.one_or_none()

    if not user:
        print(f"[DEBUG] User not found for email: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다.",
        )

    if not verify_password(password, user.hashed_password):
        print(f"[DEBUG] Invalid password for user: {email}")
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
    print(f"[DEBUG] Login successful for user: {email}, session_id: {session_id}")
    # 세션 생성 후 바로 get_user_id_from_session 호출하여 확인
    retrieved_user_id = await get_user_id_from_session(redis, session_id)
    print(f"[DEBUG] After login, retrieved user_id from session: {retrieved_user_id}")
    return {"message": "로그인 성공"}

@app.get("/auth/me", response_model=UserPublic)
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

@app.post("/auth/logout")
async def logout(
    response: Response,
    redis: Annotated[Redis, Depends(get_redis)],
    session_id: Annotated[Optional[str], Cookie()] = None
):
    if session_id:
        await delete_session(redis, session_id)
    response.delete_cookie("session_id", path="/")
    return {"message":"LOGOUT 성공"}

@app.get("/users", response_model=list[UserPublic])
async def get_all_users(session: Annotated[AsyncSession, Depends(get_session)]):
    statement = select(User)
    users = await session.exec(statement)
    return [create_user_public(user) for user in users.all()]

@app.get("/users/{user_id}", response_model=UserPublic)
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

@app.patch("/users/me", response_model=UserPublic)
async def update_my_profile(
    user_data: UserUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[int, Header(alias="X-User-Id")],
):
    """로그인된 사용자의 프로필(이메일, 자기소개) 수정"""
    db_user = await session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404, detail="User not found")

    # 제공된 데이터만 업데이트
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return create_user_public(db_user)


@app.post("/users/me/upload_image", response_model=UserPublic)
async def upload_my_profile_image(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[int, Header(alias="X-User-Id")],
    file: UploadFile
):
    print(f"[DEBUG] Uploading image for user_id: {user_id}")
    print(f"[DEBUG] File received: {file.filename}, size: {file.size}")
    db_user = await session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자가 없습니다.")
    
    # 기존 프로필 이미지 삭제
    if db_user.profile_image_url and not db_user.profile_image_url.startswith("http"):
        old_filename = os.path.basename(db_user.profile_image_url)
        old_file_path = os.path.join(PROFILE_IMAGE_DIR, old_filename)
        if os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
                print(f"[DEBUG] Deleted old profile image: {old_file_path}")
            except Exception as e:
                print(f"[ERROR] Failed to delete old profile image {old_file_path}: {e}")

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(PROFILE_IMAGE_DIR, unique_filename)
    
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(1024):
                await out_file.write(content)
        print(f"[DEBUG] File saved to: {file_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save file: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"파일 저장 실패: {e}")

    db_user.profile_image_url = f"/static/profile_images/{unique_filename}"
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    print(f"[DEBUG] User profile_image_url updated to: {db_user.profile_image_url}")
    
    return create_user_public(db_user)

@app.post("/auth/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: UpdatePassword,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    user_id: Annotated[int, Depends(get_current_user_id)],
    session_id: Annotated[Optional[str], Cookie()] = None
):
    db_user = await session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자가 없습니다.")
    if not verify_password(password_data.current_password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="비밀번호가 다릅니다.")
    
    db_user.hashed_password = get_password_hash(password_data.new_password)
    await session.commit()

    if session_id:
        await delete_session(redis, session_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)