from fastapi import APIRouter

from app.routes.auth import router as auth_router
from app.routes.conversations import router as conversations_router
from app.routes.listings import router as listings_router
from app.routes.map import router as map_router
from app.routes.users import router as users_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(conversations_router)
api_router.include_router(listings_router)
api_router.include_router(map_router)
api_router.include_router(users_router)
