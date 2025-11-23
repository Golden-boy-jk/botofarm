from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead, UserLockResponse
from app.services.user_service import (
    create_user,
    get_users as get_users_service,
    acquire_lock as acquire_lock_service,
    release_lock as release_lock_service,
    get_free_user as get_free_user_service,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=201)
async def create_user_endpoint(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Создать нового пользователя в ботоферме (async)."""
    return await create_user(db=db, user_in=user_in)


@router.get("/", response_model=List[UserRead])
async def get_users_endpoint(
    db: AsyncSession = Depends(get_db),
):
    """Получить список всех пользователей (async)."""
    return await get_users_service(db=db)


@router.get("/free", response_model=UserRead)
async def get_free_user_endpoint(
    db: AsyncSession = Depends(get_db),
):
    """Получить любого свободного (не залоченного) пользователя."""
    return await get_free_user_service(db=db)


@router.post("/{user_id}/acquire", response_model=UserLockResponse)
async def acquire_lock_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Наложить блокировку на пользователя (async)."""
    return await acquire_lock_service(db=db, user_id=user_id)


@router.post("/{user_id}/release", response_model=UserLockResponse)
async def release_lock_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Снять блокировку с пользователя (async)."""
    return await release_lock_service(db=db, user_id=user_id)
