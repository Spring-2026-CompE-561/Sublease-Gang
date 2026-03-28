from fastapi import Request

from app.errors.response import error_response


class ConflictError(Exception):
    """Raised when a resource already exists (e.g. duplicate email)."""

    def __init__(self, message: str = "Resource already exists"):
        self.message = message


async def conflict_exception_handler(_request: Request, exc: ConflictError):
    """ConflictError -> 409"""
    return error_response(
        status_code=409,
        code="conflict",
        message=exc.message,
    )
