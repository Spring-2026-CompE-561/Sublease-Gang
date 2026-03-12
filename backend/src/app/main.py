from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import api_router
from app.core.database import Base, engine
from app.core.settings import settings

# create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title = settings.app_name, 
    description = "API for Sublease Marketplace", 
    version = settings.app_version,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
