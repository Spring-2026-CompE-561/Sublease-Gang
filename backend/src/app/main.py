from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.core.settings import settings

from app.models import User, Conversation, Token, Listing

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


