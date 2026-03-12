from fastapi import APIRouter

from app.routes.conversations import router as conversations_router

api-router = APIRouter()
api_router.include_router(conversations_router)