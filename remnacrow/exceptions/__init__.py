from .base import RemnawaveError
from .client_errors import (
    ConflictError,
    FieldError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    UnauthorizedError,
    ValidationError,
)
from .server_errors import ServerError

STATUS_MAP: dict[int, type[RemnawaveError]] = {
    400: ValidationError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    429: RateLimitError,
}


def error_for_status(status: int) -> type[RemnawaveError]:
    if status in STATUS_MAP:
        return STATUS_MAP[status]
    if status >= 500:
        return ServerError
    return RemnawaveError


__all__ = [
    "ConflictError",
    "FieldError",
    "ForbiddenError",
    "NotFoundError",
    "RateLimitError",
    "RemnawaveError",
    "ServerError",
    "STATUS_MAP",
    "UnauthorizedError",
    "ValidationError",
    "error_for_status",
]
