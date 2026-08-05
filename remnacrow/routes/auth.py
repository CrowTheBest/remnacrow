from typing import Any

from ..enums import OAuth2Provider
from ..models.auth import AuthStatus, AuthToken, OAuth2AuthorizeResult
from ..models.envelope import Envelope
from .base import BaseRoute, pack


class AuthRoute(BaseRoute):
    """``/api/auth`` endpoints, mounted at ``RemnawaveClient.auth``"""

    async def login(self, username: str, password: str) -> AuthToken:
        """Authenticate with username/password (POST /api/auth/login)"""
        envelope: Envelope[AuthToken] = await self._client.request(
            "POST", "/api/auth/login",
            body=pack(username=username, password=password),
            response_type=Envelope[AuthToken],
        )
        return envelope.response

    async def register(self, username: str, password: str) -> AuthToken:
        """Register the first admin user (POST /api/auth/register)"""
        envelope: Envelope[AuthToken] = await self._client.request(
            "POST", "/api/auth/register",
            body=pack(username=username, password=password),
            response_type=Envelope[AuthToken],
        )
        return envelope.response

    async def get_status(self) -> AuthStatus:
        """Get login/register/auth provider availability (GET /api/auth/status)"""
        envelope: Envelope[AuthStatus] = await self._client.request(
            "GET", "/api/auth/status",
            response_type=Envelope[AuthStatus],
        )
        return envelope.response

    async def oauth2_authorize(self, provider: OAuth2Provider | str) -> OAuth2AuthorizeResult:
        """Build an OAuth2 authorization URL (POST /api/auth/oauth2/authorize)"""
        envelope: Envelope[OAuth2AuthorizeResult] = await self._client.request(
            "POST", "/api/auth/oauth2/authorize",
            body=pack(provider=provider),
            response_type=Envelope[OAuth2AuthorizeResult],
        )
        return envelope.response

    async def oauth2_callback(
        self,
        provider: OAuth2Provider | str,
        *,
        code: str,
        state: str,
    ) -> AuthToken:
        """Exchange OAuth2 callback code/state for an access token"""
        envelope: Envelope[AuthToken] = await self._client.request(
            "POST", "/api/auth/oauth2/callback",
            body=pack(provider=provider, code=code, state=state),
            response_type=Envelope[AuthToken],
        )
        return envelope.response

    async def get_passkey_authentication_options(self) -> dict[str, Any]:
        """Get WebAuthn authentication options for browser-side passkey login"""
        envelope: Envelope[dict[str, Any]] = await self._client.request(
            "GET", "/api/auth/passkey/authentication/options",
            response_type=Envelope[dict[str, Any]],
        )
        return envelope.response

    async def verify_passkey_authentication(self, response: dict[str, Any]) -> AuthToken:
        """Verify browser WebAuthn authentication response and return an access token"""
        envelope: Envelope[AuthToken] = await self._client.request(
            "POST", "/api/auth/passkey/authentication/verify",
            body={"response": response},
            response_type=Envelope[AuthToken],
        )
        return envelope.response
