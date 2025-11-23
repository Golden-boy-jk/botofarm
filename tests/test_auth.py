import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_token_success(
    client: AsyncClient,
    prepare_database,
) -> None:
    """
    Успешная авторизация:
    - создаём пользователя через POST /api/v1/users/
    - получаем для него токен через POST /api/v1/token
    """
    password = "MySecret123!"

    # 1. создаём пользователя
    payload = {
        "login": "auth_test@example.com",
        "password": password,
        "project_id": str(uuid.uuid4()),
        "env": "prod",
        "domain": "regular",
    }

    create_resp = await client.post("/api/v1/users/", json=payload)
    assert create_resp.status_code == 201

    # 2. запрашиваем токен
    token_resp = await client.post(
        "/api/v1/token",
        data={
            "username": payload["login"],
            "password": password,
            "grant_type": "password",  # важно для OAuth2PasswordRequestForm
        },
    )

    assert token_resp.status_code == 200

    data = token_resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_token_invalid_password(
    client: AsyncClient,
    prepare_database,
) -> None:
    """
    Неверный пароль:
    - создаём пользователя
    - пробуем получить токен с неправильным паролем
    - ожидаем 401 Unauthorized
    """
    real_password = "MySecret123!"
    wrong_password = "WrongPassword!"

    payload = {
        "login": "auth_bad@example.com",
        "password": real_password,
        "project_id": str(uuid.uuid4()),
        "env": "prod",
        "domain": "regular",
    }

    create_resp = await client.post("/api/v1/users/", json=payload)
    assert create_resp.status_code == 201

    token_resp = await client.post(
        "/api/v1/token",
        data={
            "username": payload["login"],
            "password": wrong_password,
            "grant_type": "password",
        },
    )

    assert token_resp.status_code == 401
    body = token_resp.json()
    assert body["detail"] == "Incorrect login or password"
