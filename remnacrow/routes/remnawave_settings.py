from typing import Any

from ..models.envelope import Envelope
from ..models.remnawave_settings import RemnawaveSettings
from .base import BaseRoute, pack


class RemnawaveSettingsRoute(BaseRoute):
    """``/api/remnawave-settings`` endpoints."""

    async def get_settings(self) -> RemnawaveSettings:
        envelope: Envelope[RemnawaveSettings] = await self._client.request(
            "GET",
            "/api/remnawave-settings",
            response_type=Envelope[RemnawaveSettings],
        )
        return envelope.response

    async def update_settings(
        self,
        *,
        passkey_settings: dict[str, Any] | None = None,
        oauth2_settings: dict[str, Any] | None = None,
        password_settings: dict[str, Any] | None = None,
        branding_settings: dict[str, Any] | None = None,
    ) -> RemnawaveSettings:
        body = pack(
            passkey_settings=passkey_settings,
            oauth2_settings=oauth2_settings,
            password_settings=password_settings,
            branding_settings=branding_settings,
        )
        envelope: Envelope[RemnawaveSettings] = await self._client.request(
            "PATCH",
            "/api/remnawave-settings",
            body=body,
            response_type=Envelope[RemnawaveSettings],
        )
        return envelope.response
