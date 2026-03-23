from fastapi import APIRouter

from app.routes.conversations import router as conversations_router
from app.routes.users import router as users_router
from app.routes.map import router as map_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(conversations_router)
api_router.include_router(users_router)
api_router.include_router(map_router)
