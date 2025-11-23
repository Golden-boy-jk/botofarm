from datetime import datetime, timezone, timedelta
from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User
from app.core.security import verify_password
from app.schemas.user import UserCreate, UserRead, UserLockResponse


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """
    Создать нового пользователя в ботоферме.
    Проверяем уникальность логина, хешируем пароль.
    """
    # проверка на дубликат логина
    stmt = select(User).where(User.login == user_in.login)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this login already exists.",
        )

    user = User(
        # id генерируется в модели через default=uuid4()
        created_at=datetime.now(timezone.utc),
        login=user_in.login,
        password=hash_password(user_in.password),
        project_id=user_in.project_id,
        env=user_in.env,
        domain=user_in.domain,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_users(db: AsyncSession) -> Sequence[User]:
    """
    Получить список всех пользователей, отсортированных по дате создания.
    """
    stmt = select(User).order_by(User.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_free_user(db: AsyncSession) -> User:
    """
    Получить любого свободного (не залоченного) пользователя.
    Если свободных нет — 404.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=settings.lock_timeout_seconds)

    clear_stmt = (
        update(User)
        .where(User.locktime.is_not(None))
        .where(User.locktime < cutoff)
        .values(locktime=None)
    )
    await db.execute(clear_stmt)
    await db.commit()

    stmt = (
        select(User)
        .where(User.locktime.is_(None))
        .order_by(User.created_at.asc())
        .limit(1)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No free users available.",
        )

    return user

async def acquire_lock(db: AsyncSession, user_id: UUID) -> UserLockResponse:
    """
    Наложить блокировку на пользователя.
    Если пользователя нет → 404.
    Если уже заблокирован → 409.
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if user.locktime is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already locked.",
        )

    user.locktime = datetime.now(timezone.utc)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserLockResponse(
        id=user.id,
        locked=True,
        locktime=user.locktime,
        message="User successfully locked.",
    )


async def release_lock(db: AsyncSession, user_id: UUID) -> UserLockResponse:
    """
    Снять блокировку с пользователя.
    Если пользователя нет → 404.
    Если не был заблокирован → просто сообщаем об этом.
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if user.locktime is None:
        # не считаем это ошибкой, просто возвращаем статус
        return UserLockResponse(
            id=user.id,
            locked=False,
            locktime=None,
            message="User was not locked.",
        )

    user.locktime = None
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserLockResponse(
        id=user.id,
        locked=False,
        locktime=None,
        message="User successfully unlocked.",
    )


async def get_user_by_login(db: AsyncSession, login: str) -> User | None:
    stmt = select(User).where(User.login == login)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, login: str, password: str) -> User | None:
    """
    Проверка логина и пароля:
    - находим пользователя по логину
    - сверяем пароль через verify_password
    """
    user = await get_user_by_login(db, login=login)
    if user is None:
        return None

    if not verify_password(password, user.password):
        return None

    return user