from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    login: EmailStr
    project_id: UUID
    env: str = Field(..., description="Окружение: prod, preprod, stage")
    domain: str = Field(..., description="Тип пользователя: canary, regular")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserRead(UserBase):
    id: UUID
    created_at: datetime
    locktime: Optional[datetime] = None

    class Config:
        from_attributes = True  # для работы с ORM-моделями


class UserLockResponse(BaseModel):
    id: UUID
    locked: bool
    locktime: Optional[datetime]
    message: str
