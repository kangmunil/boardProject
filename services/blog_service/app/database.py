import os
from dotenv import load_dotenv
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

# .env 파일 로드
load_dotenv()
DATABASE_URL=os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True) 

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session():
    async with AsyncSession(engine) as session:
        yield session # 중간에 결과를 잠깐 내보내고, 함수가 끝날 때까지 대기