import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import api_router
from app.core.database import Base, engine
from app.core.settings import settings
from app.middleware import (
    LoggingMiddleware,
    RateLimitMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
)
from fastapi.exceptions import RequestValidationError

from app.errors.auth import AuthError, auth_exception_handler
from app.errors.conflict import ConflictError, conflict_exception_handler
from app.errors.not_found import NotFoundError, not_found_exception_handler
from app.errors.permission import PermissionError, permission_exception_handler
from app.errors.server import server_exception_handler
from app.errors.validation import validation_exception_handler
from app.models import Conversation, Listing, Profile, Token, User

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

# create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="API for Sublease Marketplace",
    version=settings.app_version,
)

# Request ID 
app.add_middleware(RequestIDMiddleware)

# Logging 
app.add_middleware(LoggingMiddleware)

# Security headers
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting 
app.add_middleware(RateLimitMiddleware)

# CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(AuthError, auth_exception_handler)
app.add_exception_handler(PermissionError, permission_exception_handler)
app.add_exception_handler(NotFoundError, not_found_exception_handler)
app.add_exception_handler(ConflictError, conflict_exception_handler)
app.add_exception_handler(Exception, server_exception_handler)

app.include_router(api_router)
