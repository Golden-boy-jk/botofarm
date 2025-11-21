import uuid
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.db.base import Base
from app.db.session import get_db


# ---- Настраиваем тестовую БД (SQLite вместо Postgres) ----

SQLALCHEMY_DATABASE_URL = "sqlite:///./tests.db"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test,
    class_=Session,
)


def override_get_db() -> Generator[Session, None, None]:
    """Заменяем зависимость get_db на тестовую сессию."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Подменяем зависимость во всём приложении
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """
    Создаём чистую БД перед каждым тестом и дропаем после.

    В начале было по-другому и первый тест
    test_create_user_success отбивал 201 всё ОК.
    Второй тест test_create_user_duplicate_login снова делает
    POST /api/v1/users/ с тем же login,
    но в БД уже есть запись от первого теста,
    сервис кидает HTTPException(400, "User with this login already exists.")
    поэтому первый assert response_1.status_code == 201 и падает, потому что уже 400.
    То есть тесты зависят друг от друга, а это плохо.
    Для дублей мы хотим, чтобы внутри одного теста первый запрос прошёл (201),
    а второй уже упал (400).
    """
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Отдельная сессия БД для теста (если понадобится напрямую)."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client() -> TestClient:
    """Клиент FastAPI для обращения к API."""
    return TestClient(app)


@pytest.fixture
def user_payload():
    """Базовый payload для создания пользователя."""
    return {
        "login": "testuser@example.com",
        "password": "secret123",
        "project_id": str(uuid.uuid4()),
        "env": "prod",
        "domain": "regular",
    }
