pytest_plugins = ("pytest_asyncio",)

from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from app.main import app
from app.db.base import Base
from app.db.session import get_db


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


engine_test = create_async_engine(
    TEST_DATABASE_URL,
    future=True,
    echo=False,
)

AsyncSessionLocalTest = async_sessionmaker(
    bind=engine_test,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocalTest() as session:
        yield session


@pytest.fixture(scope="function")
async def prepare_database():
    # Полная очистка SQLite перед каждым тестом
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Подмена продовой get_db на тестовую
    app.dependency_overrides[get_db] = override_get_db

    yield


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
