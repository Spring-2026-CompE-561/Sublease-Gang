from fastapi import Request
from fastapi.exceptions import RequestValidationError

from app.errors.response import error_response


async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    """RequestValidationError (Pydantic) -> 400"""
    details = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err["loc"] if loc != "body")
        details.append({"field": field, "issue": err["msg"]})

    return error_response(
        status_code=400,
        code="validation_error",
        message="One or more fields are invalid",
        details=details,
    )
