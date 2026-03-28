from fastapi import Request

from app.errors.response import error_response


class PermissionError(Exception):
    """Raised when the authenticated user does not own the resource."""

    def __init__(self, message: str = "You do not have permission to perform this action"):
        self.message = message


async def permission_exception_handler(_request: Request, exc: PermissionError):
    """PermissionError -> 403"""
    return error_response(
        status_code=403,
        code="permission_error",
        message=exc.message,
    )
