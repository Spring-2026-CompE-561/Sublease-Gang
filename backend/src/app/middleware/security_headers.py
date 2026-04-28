from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.settings import settings

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), camera=(), microphone=()",
}

if settings.environment == "production":
    SECURITY_HEADERS["Strict-Transport-Security"] = (
        "max-age=63072000; includeSubDomains"
    )

# Routes that should have Cache-Control: no-store
_SENSITIVE_PREFIXES = ("/api/v1/auth/", "/api/v1/users/me")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add common security headers to every response for browser-level protection."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        response = await call_next(request)
        for header, value in SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)

        # Only apply no-store to sensitive endpoints
        if any(request.url.path.startswith(p) for p in _SENSITIVE_PREFIXES):
            response.headers.setdefault("Cache-Control", "no-store")

        return response
