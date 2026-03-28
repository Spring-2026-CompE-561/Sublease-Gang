from fastapi import Request

from app.errors.response import error_response


class AuthError(Exception):
    """Raised when authentication fails (invalid/missing token)."""

    def __init__(self, message: str = "Invalid or missing authentication token"):
        self.message = message


async def auth_exception_handler(_request: Request, exc: AuthError):
    """AuthError -> 401"""
    return error_response(
        status_code=401,
        code="auth_error",
        message=exc.message,
    )
