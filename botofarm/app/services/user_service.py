from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserLockResponse


def create_user(db: Session, user_in: UserCreate) -> User:
    """Создать нового пользователя в ботоферме."""
    # проверяем уникальность логина
    existing = db.query(User).filter(User.login == user_in.login).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this login already exists.",
        )

    db_user = User(
        login=user_in.login,
        password=hash_password(user_in.password),
        project_id=user_in.project_id,
        env=user_in.env,
        domain=user_in.domain,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session) -> List[User]:
    """Получить всех пользователей ботофермы."""
    return db.query(User).order_by(User.created_at.desc()).all()


def acquire_lock(db: Session, user_id: UUID) -> UserLockResponse:
    """Наложить блокировку на пользователя.

    Если пользователь уже заблокирован (locktime не NULL),
    вернуть ошибку 409.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if user.locktime is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already locked.",
        )

    user.locktime = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserLockResponse(
        id=user.id,
        locked=True,
        locktime=user.locktime,
        message="User successfully locked.",
    )


def release_lock(db: Session, user_id: UUID) -> UserLockResponse:
    """Снять блокировку с пользователя (обнулить locktime)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if user.locktime is None:
        # Не ошибка, но даём понятный ответ
        return UserLockResponse(
            id=user.id,
            locked=False,
            locktime=None,
            message="User was not locked.",
        )

    user.locktime = None
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserLockResponse(
        id=user.id,
        locked=False,
        locktime=None,
        message="User successfully unlocked.",
    )
