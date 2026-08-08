from typing import Any

from .base import Struct


class EntityMetadata(Struct):
    metadata: dict[str, Any]
