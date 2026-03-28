import logging

from fastapi import Request

from app.errors.response import error_response

logger = logging.getLogger(__name__)


async def server_exception_handler(_request: Request, exc: Exception):
    """Catch-all for unhandled exceptions -> 500"""
    logger.exception("Unexpected server error: %s", exc)
    return error_response(
        status_code=500,
        code="server_error",
        message="An unexpected error occurred",
    )
