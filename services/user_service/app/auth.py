import secrets
from typing import Optional
from passlib.context import CryptContext
from redis.asyncio import Redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SESSION_TTL_SECONDS = 3600

def verify_password(plain_password:str, hashed_password:str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password:str) -> str:
    return pwd_context.hash(password)

async def create_session(redis: Redis, user_id:int) -> str:
    session_id = secrets.token_hex(16)
    redis_key = f"session:{session_id}"
    user_id_str = str(user_id)
    print(f"[DEBUG] create_session: Setting key='{redis_key}', value='{user_id_str}', ttl={SESSION_TTL_SECONDS}")
    await redis.setex(redis_key, SESSION_TTL_SECONDS, user_id_str)
    # 한시간 후에 세션이 지워지도록 설정
    return session_id
async def get_user_id_from_session(redis,session_id) -> Optional[int]:
    print(f"[DEBUG] get_user_id_from_session: Received session_id = {session_id}")
    user_id_str = await redis.get(f"session:{session_id}")
    print(f"[DEBUG] get_user_id_from_session: Retrieved user_id from Redis = {user_id_str}")
    return int(user_id_str) if user_id_str else None

async def delete_session(redis: Redis, session_id: str):
    await redis.delete(f"session:{session_id}")