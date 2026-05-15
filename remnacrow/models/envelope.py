from typing import Generic, TypeVar

from .base import Struct

T = TypeVar("T")


class Envelope(Struct, Generic[T]):
    """Remnawave wraps all responses as {"response": <payload>}"""
    response: T
