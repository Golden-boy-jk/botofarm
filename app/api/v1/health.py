from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter(tags=["health"])


async def _check_db(db: AsyncSession) -> dict:
    """
    Проверка доступности БД.
    Делаем простой SELECT 1 через текущую async-сессию.
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:
        # В логах всё равно будет traceback от uvicorn
        return {"status": "error", "error": str(exc)}


@router.get("/health", summary="Healthcheck сервиса")
async def healthcheck(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Продовый healthcheck:
    - проверка работы приложения
    - проверка доступности БД
    """
    db_status = await _check_db(db)
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
