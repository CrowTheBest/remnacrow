from datetime import datetime
from typing import Any

from .base import RemnawaveError


class ServerError(RemnawaveError):
    """5xx — panel-side failure

    The panel sends a structured payload for server errors:
    ``{timestamp, path, message, errorCode}``. The most useful bits are
    exposed as attributes for programmatic access and log correlation.
    """

    error_code: str | None
    path: str | None
    timestamp: datetime | None

    def __init__(
        self,
        message: str = "",
        *,
        status_code: int | None = None,
        payload: Any = None,
    ) -> None:
        self.error_code = None
        self.path = None
        self.timestamp = None

        if isinstance(payload, dict):
            error_code = payload.get("errorCode")
            self.error_code = str(error_code) if error_code is not None else None

            request_path = payload.get("path")
            self.path = str(request_path) if request_path is not None else None

            timestamp = payload.get("timestamp")
            if isinstance(timestamp, str):
                try:
                    self.timestamp = datetime.fromisoformat(timestamp)
                except ValueError:
                    self.timestamp = None

        if self.error_code:
            message = f"[{self.error_code}] {message}" if message else f"[{self.error_code}]"
        super().__init__(message, status_code=status_code, payload=payload)
