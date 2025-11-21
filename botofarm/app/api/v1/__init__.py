from fastapi import APIRouter

from app.api.v1 import users, health

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(health.router)
