import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_free_user(
    client: AsyncClient,
    prepare_database,
) -> None:
    """
    Проверяем, что:
    - пользователь создаётся через POST /api/v1/users/
    - /api/v1/users/free возвращает свободного пользователя
    """
    payload = {
        "login": f"free_{uuid.uuid4().hex[:6]}@example.com",
        "password": "secret123",
        "project_id": str(uuid.uuid4()),
        "env": "prod",
        "domain": "regular",
    }

    # создаём юзера
    resp_create = await client.post("/api/v1/users/", json=payload)
    assert resp_create.status_code == 201

    # получаем свободного юзера
    resp_free = await client.get("/api/v1/users/free")
    assert resp_free.status_code == 200

    data = resp_free.json()

    # сравниваем логины
    assert data["login"] == payload["login"]


@pytest.mark.asyncio
async def test_get_all_users(
    client: AsyncClient,
    prepare_database,
) -> None:
    """
    Проверяем, что:
    - можно создать несколько пользователей
    - GET /api/v1/users/ возвращает их в списке
    """
    payload1 = {
        "login": "test1@example.com",
        "password": "secret",
        "project_id": "111",
        "env": "prod",
        "domain": "regular",
    }

    payload2 = {
        "login": "test2@example.com",
        "password": "secret",
        "project_id": "222",
        "env": "prod",
        "domain": "regular",
    }

    r1 = await client.post("/api/v1/users/", json=payload1)
    r2 = await client.post("/api/v1/users/", json=payload2)

    assert r1.status_code == 201
    assert r2.status_code == 201

    # проверяем новый эндпоинт
    resp = await client.get("/api/v1/users/")
    assert resp.status_code == 200

    data = resp.json()
    emails = [u["login"] for u in data]

    assert "test1@example.com" in emails
    assert "test2@example.com" in emails
