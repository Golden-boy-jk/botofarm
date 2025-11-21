from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.db.session import engine

router = APIRouter(tags=["health"])


async def _check_db() -> dict:
    """
    Проверка доступности БД.
    Делаем простой SELECT 1 через async-connection.
    """
    try:
        async with engine.connect() as conn:  # type: AsyncConnection
            await conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:
        # В логах ты всё равно увидишь traceback от uvicorn
        return {"status": "error", "error": str(exc)}


@router.get("/health", summary="Healthcheck сервиса")
async def healthcheck() -> dict:
    """
    Продовый healthcheck:
    - проверка работы приложения
    - проверка доступности БД
    """
    db_status = await _check_db()

    overall_ok = db_status["status"] == "ok"

    if not overall_ok:
        # 503 — сервис временно недоступен
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"db": db_status},
        )

    return {
        "status": "ok",
        "time": datetime.now(timezone.utc).isoformat(),
        "db": db_status,
    }
