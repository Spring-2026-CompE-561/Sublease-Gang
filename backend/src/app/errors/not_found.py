from fastapi import Request

from app.errors.response import error_response


class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "Resource not found"):
        self.message = message


async def not_found_exception_handler(_request: Request, exc: NotFoundError):
    """NotFoundError -> 404"""
    return error_response(
        status_code=404,
        code="not_found",
        message=exc.message,
    )
