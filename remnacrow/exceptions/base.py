from typing import Any


class RemnawaveError(Exception):
    """Base class for all Remnawave API errors"""

    def __init__(
        self,
        message: str = "",
        *,
        status_code: int | None = None,
        payload: Any = None,
    ) -> None:
        self.status_code = status_code
        self.payload = payload
        super().__init__(message or self.__class__.__name__)