import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_free_user(client: AsyncClient):
    # создаём пользователя, который точно свободен
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
