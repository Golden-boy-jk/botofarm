from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from app.core.config import settings


# Async-движок для SQLAlchemy
engine = create_async_engine(
    settings.async_database_url,
    echo=settings.debug,
    future=True,
)


# Фабрика async-сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для FastAPI: получить async-сессию БД
    и корректно её закрыть.
    """
    async with AsyncSessionLocal() as session:
        yield session