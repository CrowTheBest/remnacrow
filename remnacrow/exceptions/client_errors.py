from dataclasses import dataclass, field
from typing import Any

from .base import RemnawaveError


@dataclass
class FieldError:
    """One field-level validation issue returned by the panel in ``errors[]``"""

    path: list[str]
    code: str
    message: str
    extra: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        loc = ".".join(self.path) if self.path else "<root>"
        return f"{loc}: {self.message}"


def _parse_field_errors(payload: Any) -> list[FieldError]:
    """Pull the structured ``errors`` array from a panel error payload"""
    if not isinstance(payload, dict):
        return []
    items = payload.get("errors") or []
    if not isinstance(items, list):
        return []

    parsed: list[FieldError] = []
    for item in items:
        if not isinstance(item, dict):
            continue

        path = item.get("path")
        parsed.append(FieldError(
            path=[str(p) for p in path] if isinstance(path, list) else [],
            code=str(item.get("code", "")),
            message=str(item.get("message", "")),
            extra={
                key: value for key, value in item.items()
                if key not in ("path", "code", "message")
            },
        ))
    return parsed


class ValidationError(RemnawaveError):
    """400 — request validation failed

    Exposes a structured list of per-field issues in :attr:`errors`.
    """

    errors: list[FieldError]

    def __init__(
        self,
        message: str = "",
        *,
        status_code: int | None = None,
        payload: Any = None,
    ) -> None:
        self.errors = _parse_field_errors(payload)
        if self.errors:
            details = "; ".join(str(e) for e in self.errors)
            message = f"{message} — {details}" if message else details
        super().__init__(message, status_code=status_code, payload=payload)


class UnauthorizedError(RemnawaveError):
    """401 — invalid or missing token"""


class ForbiddenError(RemnawaveError):
    """403 — token lacks permission"""


class NotFoundError(RemnawaveError):
    """404 — entity not found"""


class ConflictError(RemnawaveError):
    """409 — entity already exists / state conflict"""


class RateLimitError(RemnawaveError):
    """429 — too many requests"""
