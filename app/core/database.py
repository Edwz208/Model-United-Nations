# app/core/database.py

from collections.abc import AsyncGenerator

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.settings import get_settings

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True, connect_args={"statement_cache_size": 0})
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session