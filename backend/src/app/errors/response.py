from fastapi.responses import JSONResponse


def error_response(status_code: int, code: str, message: str, details: list | None = None) -> JSONResponse:
    """Build a standardized error response."""
    body: dict = {
        "error": {
            "code": code,
            "message": message,
        }
    }
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body)
