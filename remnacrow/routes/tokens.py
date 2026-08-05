from ..models.envelope import Envelope
from ..models.tokens import ApiTokenScopes, ApiTokenWithSecret, ApiTokensResult
from .base import BaseRoute, pack


class TokensRoute(BaseRoute):
    """``/api/tokens`` endpoints, mounted at ``RemnawaveClient.tokens``"""

    async def get_tokens(self) -> ApiTokensResult:
        """List API tokens and docs links (GET /api/tokens)"""
        envelope: Envelope[ApiTokensResult] = await self._client.request(
            "GET", "/api/tokens",
            response_type=Envelope[ApiTokensResult],
        )
        return envelope.response

    async def create_token(
        self,
        name: str,
        *,
        expires_in_days: int | float,
        scopes: list[str] | None = None,
    ) -> ApiTokenWithSecret:
        """Create an API token (POST /api/tokens)"""
        envelope: Envelope[ApiTokenWithSecret] = await self._client.request(
            "POST", "/api/tokens",
            body=pack(name=name, expires_in_days=expires_in_days, scopes=scopes),
            response_type=Envelope[ApiTokenWithSecret],
        )
        return envelope.response

    async def get_scopes(self) -> ApiTokenScopes:
        """List API-token scopes (GET /api/tokens/scopes)"""
        envelope: Envelope[ApiTokenScopes] = await self._client.request(
            "GET", "/api/tokens/scopes",
            response_type=Envelope[ApiTokenScopes],
        )
        return envelope.response

    async def delete_token(self, uuid: str) -> bool:
        """Delete an API token by uuid (DELETE /api/tokens/{uuid})"""
        envelope: Envelope[bool] = await self._client.request(
            "DELETE", f"/api/tokens/{uuid}",
            response_type=Envelope[bool],
        )
        return envelope.response
