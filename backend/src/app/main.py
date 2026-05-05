import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.routes import api_router
from app.core.database import Base, engine
from app.core.settings import settings
from app.errors.auth import AuthError, auth_exception_handler
from app.errors.conflict import ConflictError, conflict_exception_handler
from app.errors.not_found import NotFoundError, not_found_exception_handler
from app.errors.permission import PermissionError, permission_exception_handler
from app.errors.server import server_exception_handler
from app.errors.validation import validation_exception_handler
from app.middleware import (
    BodySizeLimitMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
)

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

# create DB tables
Base.metadata.create_all(bind=engine)

_is_prod = settings.environment == "production"

app = FastAPI(
    title=settings.app_name,
    description="API for Sublease Marketplace",
    version=settings.app_version,
    # Hide interactive docs in production — they ease recon and pull
    # external CDN scripts that don't fit a strict API CSP.
    docs_url=None if _is_prod else "/docs",
    redoc_url=None if _is_prod else "/redoc",
    openapi_url=None if _is_prod else "/openapi.json",
)

# Request ID
app.add_middleware(RequestIDMiddleware)

# Logging
app.add_middleware(LoggingMiddleware)

# Security headers
app.add_middleware(SecurityHeadersMiddleware)

# Body size limit (fast-fail on oversized payloads before they reach handlers)
app.add_middleware(
    BodySizeLimitMiddleware,
    max_bytes=settings.max_request_body_bytes,
)

# Rate limiting
app.add_middleware(
    RateLimitMiddleware,
    trusted_proxies=settings.trusted_proxies,
)

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

# Local-disk media storage for uploaded assets (profile icons, etc.).
# TODO: swap to object storage (S3/R2) before deploy.
MEDIA_DIR = Path("media")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")
