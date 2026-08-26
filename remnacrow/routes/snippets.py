from typing import Any

from ..models.envelope import Envelope
from ..models.snippets import SnippetsPage
from .base import BaseRoute


class SnippetsRoute(BaseRoute):
    """``/api/snippets`` endpoints."""

    async def get_snippets(self) -> SnippetsPage:
        envelope: Envelope[SnippetsPage] = await self._client.request(
            "GET",
            "/api/snippets",
            response_type=Envelope[SnippetsPage],
        )
        return envelope.response

    async def delete_snippet(self, name: str) -> SnippetsPage:
        envelope: Envelope[SnippetsPage] = await self._client.request(
            "DELETE",
            "/api/snippets",
            body={"name": name},
            response_type=Envelope[SnippetsPage],
        )
        return envelope.response

    async def create_snippet(self, name: str, snippet: list[dict[str, Any]]) -> SnippetsPage:
        envelope: Envelope[SnippetsPage] = await self._client.request(
            "POST",
            "/api/snippets",
            body={"name": name, "snippet": snippet},
            response_type=Envelope[SnippetsPage],
        )
        return envelope.response

    async def update_snippet(self, name: str, snippet: list[dict[str, Any]]) -> SnippetsPage:
        envelope: Envelope[SnippetsPage] = await self._client.request(
            "PATCH",
            "/api/snippets",
            body={"name": name, "snippet": snippet},
            response_type=Envelope[SnippetsPage],
        )
        return envelope.response
