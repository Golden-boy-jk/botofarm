from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead, UserLockResponse
from app.services.user_service import (
    create_user,
    get_users as get_users_service,
    acquire_lock as acquire_lock_service,
    release_lock as release_lock_service,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=201)
def create_user_endpoint(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """Создать нового пользователя в ботоферме."""
    user = create_user(db=db, user_in=user_in)
    return user


@router.get("/", response_model=List[UserRead])
def get_users_endpoint(
    db: Session = Depends(get_db),
):
    """Получить список всех пользователей."""
    users = get_users_service(db=db)
    return users


@router.post("/{user_id}/acquire", response_model=UserLockResponse)
def acquire_lock_endpoint(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    """Наложить блокировку на пользователя."""
    return acquire_lock_service(db=db, user_id=user_id)


@router.post("/{user_id}/release", response_model=UserLockResponse)
def release_lock_endpoint(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    """Снять блокировку с пользователя."""
    return release_lock_service(db=db, user_id=user_id)
