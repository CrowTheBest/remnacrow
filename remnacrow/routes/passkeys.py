from typing import Any

from ..models.envelope import Envelope
from ..models.passkeys import Passkey, PasskeyRegistrationResult, PasskeysResult
from .base import BaseRoute, pack


class PasskeysRoute(BaseRoute):
    """``/api/passkeys`` endpoints, mounted at ``RemnawaveClient.passkeys``"""

    async def get_passkeys(self) -> list[Passkey]:
        """List active passkeys for the current admin (GET /api/passkeys)"""
        envelope: Envelope[PasskeysResult] = await self._client.request(
            "GET", "/api/passkeys",
            response_type=Envelope[PasskeysResult],
        )
        return envelope.response.passkeys

    async def update_passkey(self, id: str, name: str) -> list[Passkey]:
        """Rename a passkey (PATCH /api/passkeys)"""
        envelope: Envelope[PasskeysResult] = await self._client.request(
            "PATCH", "/api/passkeys",
            body=pack(id=id, name=name),
            response_type=Envelope[PasskeysResult],
        )
        return envelope.response.passkeys

    async def delete_passkey(self, id: str) -> list[Passkey]:
        """Delete a passkey (DELETE /api/passkeys)"""
        envelope: Envelope[PasskeysResult] = await self._client.request(
            "DELETE", "/api/passkeys",
            body=pack(id=id),
            response_type=Envelope[PasskeysResult],
        )
        return envelope.response.passkeys

    async def get_registration_options(self) -> dict[str, Any]:
        """Get WebAuthn registration options for browser-side passkey creation"""
        envelope: Envelope[dict[str, Any]] = await self._client.request(
            "GET", "/api/passkeys/registration/options",
            response_type=Envelope[dict[str, Any]],
        )
        return envelope.response

    async def verify_registration(self, response: dict[str, Any]) -> bool:
        """Verify browser WebAuthn registration response"""
        envelope: Envelope[PasskeyRegistrationResult] = await self._client.request(
            "POST", "/api/passkeys/registration/verify",
            body={"response": response},
            response_type=Envelope[PasskeyRegistrationResult],
        )
        return envelope.response.verified
