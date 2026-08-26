from typing import Any

from .base import Struct


class Snippet(Struct):
    name: str
    snippet: Any


class SnippetsPage(Struct):
    total: int
    snippets: list[Snippet]
