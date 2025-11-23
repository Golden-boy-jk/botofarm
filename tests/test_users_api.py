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
        "project_id": str(uuid.uuid4()),  # UUID проекта
        "env": "prod",
        "domain": "regular",
    }

    # создаём пользователя
    resp_create = await client.post("/api/v1/users/", json=payload)
    assert resp_create.status_code == 201

    # получаем свободного юзера
    resp_free = await client.get("/api/v1/users/free")
    assert resp_free.status_code == 200

    data = resp_free.json()

    # сравниваем логины (должен вернуться тот, кого только что создали)
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
        "project_id": str(uuid.uuid4()),
        "env": "prod",
        "domain": "regular",
    }
    payload2 = {
        "login": "test2@example.com",
        "password": "secret",
        "project_id": str(uuid.uuid4()),
        "env": "prod",
        "domain": "regular",
    }

    r1 = await client.post("/api/v1/users/", json=payload1)
    r2 = await client.post("/api/v1/users/", json=payload2)

    assert r1.status_code == 201
    assert r2.status_code == 201

    # запрашиваем список всех пользователей
    resp = await client.get("/api/v1/users/")
    assert resp.status_code == 200

    data = resp.json()
    emails = [u["login"] for u in data]

    assert "test1@example.com" in emails
    assert "test2@example.com" in emails


@pytest.mark.asyncio
async def test_acquire_and_release_lock(
    client: AsyncClient,
    prepare_database,
) -> None:
    """
    Проверяем happy-path:
    - создаём пользователя
    - накладываем блокировку /acquire
    - снимаем блокировку /release
    """
    payload = {
        "login": f"lock_{uuid.uuid4().hex[:6]}@example.com",
        "password": "secret123",
        "project_id": str(uuid.uuid4()),
        "env": "prod",
        "domain": "regular",
    }

    # создаём пользователя
    resp_create = await client.post("/api/v1/users/", json=payload)
    assert resp_create.status_code == 201

    created = resp_create.json()
    user_id = created["id"]

    # накладываем блокировку
    resp_acquire = await client.post(f"/api/v1/users/{user_id}/acquire")
    assert resp_acquire.status_code == 200

    # можно дополнительно проверить тело ответа, если хочешь:
    # data_acquire = resp_acquire.json()
    # assert data_acquire["id"] == user_id

    # снимаем блокировку
    resp_release = await client.post(f"/api/v1/users/{user_id}/release")
    assert resp_release.status_code == 200

    # и снова можно проверить тело ответа, если схема UserLockResponse это позволяет
    # data_release = resp_release.json()
    # assert data_release["id"] == user_id


@pytest.mark.asyncio
async def test_acquire_lock_twice_fails(
    client: AsyncClient,
    prepare_database,
) -> None:
    """
    Проверяем, что:
    - первый acquire проходит успешно
    - повторный acquire для того же пользователя возвращает ошибку
      (конкретный код можно подправить под реализацию: 400 / 409 / 423 и т.п.)
    """
    payload = {
        "login": f"busy_{uuid.uuid4().hex[:6]}@example.com",
        "password": "secret123",
        "project_id": str(uuid.uuid4()),
        "env": "prod",
        "domain": "regular",
    }

    # создаём пользователя
    resp_create = await client.post("/api/v1/users/", json=payload)
    assert resp_create.status_code == 201
    user_id = resp_create.json()["id"]

    # первый acquire — ок
    resp_acquire_1 = await client.post(f"/api/v1/users/{user_id}/acquire")
    assert resp_acquire_1.status_code == 200

    # повторный acquire — должен вернуть ошибку (пользователь уже занят)
    resp_acquire_2 = await client.post(f"/api/v1/users/{user_id}/acquire")

    # Если знаешь точный код (например, 409), можно сделать строго:
    # assert resp_acquire_2.status_code == 409
    # Пока что делаем мягко, лишь бы был неуспех
    assert resp_acquire_2.status_code >= 400
    assert resp_acquire_2.status_code != 200
