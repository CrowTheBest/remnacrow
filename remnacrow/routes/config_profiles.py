from typing import Any

from ..models.common import DeletedResult
from ..models.config_profiles import (
    ConfigProfile,
    ConfigProfileInboundsPage,
    ConfigProfilesPage,
)
from ..models.envelope import Envelope
from .base import BaseRoute, pack


class ConfigProfilesRoute(BaseRoute):
    """``/api/config-profiles`` endpoints."""

    async def get_config_profiles(self) -> ConfigProfilesPage:
        envelope: Envelope[ConfigProfilesPage] = await self._client.request(
            "GET",
            "/api/config-profiles",
            response_type=Envelope[ConfigProfilesPage],
        )
        return envelope.response

    async def create_config_profile(self, name: str, config: dict[str, Any]) -> ConfigProfile:
        envelope: Envelope[ConfigProfile] = await self._client.request(
            "POST",
            "/api/config-profiles",
            body={"name": name, "config": config},
            response_type=Envelope[ConfigProfile],
        )
        return envelope.response

    async def update_config_profile(
        self,
        uuid: str,
        *,
        name: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> ConfigProfile:
        body = pack(uuid=uuid, name=name, config=config)
        envelope: Envelope[ConfigProfile] = await self._client.request(
            "PATCH",
            "/api/config-profiles",
            body=body,
            response_type=Envelope[ConfigProfile],
        )
        return envelope.response

    async def get_all_inbounds(self) -> ConfigProfileInboundsPage:
        envelope: Envelope[ConfigProfileInboundsPage] = await self._client.request(
            "GET",
            "/api/config-profiles/inbounds",
            response_type=Envelope[ConfigProfileInboundsPage],
        )
        return envelope.response

    async def get_inbounds_by_profile_uuid(self, uuid: str) -> ConfigProfileInboundsPage:
        envelope: Envelope[ConfigProfileInboundsPage] = await self._client.request(
            "GET",
            f"/api/config-profiles/{uuid}/inbounds",
            response_type=Envelope[ConfigProfileInboundsPage],
        )
        return envelope.response

    async def get_config_profile_by_uuid(self, uuid: str) -> ConfigProfile:
        envelope: Envelope[ConfigProfile] = await self._client.request(
            "GET",
            f"/api/config-profiles/{uuid}",
            response_type=Envelope[ConfigProfile],
        )
        return envelope.response

    async def delete_config_profile(self, uuid: str) -> bool:
        envelope: Envelope[DeletedResult] = await self._client.request(
            "DELETE",
            f"/api/config-profiles/{uuid}",
            response_type=Envelope[DeletedResult],
        )
        return envelope.response.is_deleted

    async def get_computed_config_profile_by_uuid(self, uuid: str) -> ConfigProfile:
        envelope: Envelope[ConfigProfile] = await self._client.request(
            "GET",
            f"/api/config-profiles/{uuid}/computed-config",
            response_type=Envelope[ConfigProfile],
        )
        return envelope.response

    async def reorder_config_profiles(self, order: dict[str, int]) -> ConfigProfilesPage:
        body = {
            "items": [
                {"uuid": profile_uuid, "viewPosition": position}
                for profile_uuid, position in order.items()
            ]
        }
        envelope: Envelope[ConfigProfilesPage] = await self._client.request(
            "POST",
            "/api/config-profiles/actions/reorder",
            body=body,
            response_type=Envelope[ConfigProfilesPage],
        )
        return envelope.response
