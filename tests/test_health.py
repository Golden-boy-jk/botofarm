import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_ok(client: AsyncClient, prepare_database):
    """
    /api/v1/health должен вернуть 200 и корректное тело ответа,
    если приложение и база данных живы.
    """
    resp = await client.get("/api/v1/health")

    # HTTP-статус
    assert resp.status_code == 200

    data = resp.json()

    # Общий статус
    assert data["status"] == "ok"

    # Есть время и оно строка
    assert "time" in data
    assert isinstance(data["time"], str)

    # Проверка блока db
    assert "db" in data
    assert isinstance(data["db"], dict)
    assert data["db"]["status"] == "ok"
