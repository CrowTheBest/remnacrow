from typing import Any

from ..models.envelope import Envelope
from ..models.metadata import EntityMetadata
from .base import BaseRoute


class MetadataRoute(BaseRoute):
    """``/api/metadata`` endpoints, mounted at ``RemnawaveClient.metadata``"""

    async def get_user_metadata(self, uuid: str) -> dict[str, Any]:
        """Get arbitrary metadata attached to a user."""
        envelope: Envelope[EntityMetadata] = await self._client.request(
            "GET",
            f"/api/metadata/user/{uuid}",
            response_type=Envelope[EntityMetadata],
        )
        return envelope.response.metadata

    async def upsert_user_metadata(
        self,
        uuid: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Create or replace arbitrary metadata attached to a user."""
        envelope: Envelope[EntityMetadata] = await self._client.request(
            "PUT",
            f"/api/metadata/user/{uuid}",
            body={"metadata": metadata},
            response_type=Envelope[EntityMetadata],
        )
        return envelope.response.metadata

    async def get_node_metadata(self, uuid: str) -> dict[str, Any]:
        """Get arbitrary metadata attached to a node."""
        envelope: Envelope[EntityMetadata] = await self._client.request(
            "GET",
            f"/api/metadata/node/{uuid}",
            response_type=Envelope[EntityMetadata],
        )
        return envelope.response.metadata

    async def upsert_node_metadata(
        self,
        uuid: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """Create or replace arbitrary metadata attached to a node."""
        envelope: Envelope[EntityMetadata] = await self._client.request(
            "PUT",
            f"/api/metadata/node/{uuid}",
            body={"metadata": metadata},
            response_type=Envelope[EntityMetadata],
        )
        return envelope.response.metadata
