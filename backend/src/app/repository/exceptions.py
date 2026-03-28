class ResourceNotFoundError(Exception):
    """Raised when a referenced or requested resource does not exist."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class PermissionDeniedError(Exception):
    """Raised when the caller is not allowed to perform the requested action."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class ResourceConflictError(Exception):
    """Raised when a create/update would violate a uniqueness or existence constraint."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)
