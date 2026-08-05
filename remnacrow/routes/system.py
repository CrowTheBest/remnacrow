from typing import Any

from ..models.envelope import Envelope
from ..models.system import (
    NodesMetrics,
    PublicKey,
    RemnawaveHealth,
    RemnawaveMetadata,
    SrrMatcherResponseRules,
    SrrMatcherResult,
    X25519Keypairs,
)
from .base import BaseRoute, pack


class SystemRoute(BaseRoute):
    """``/api/system`` utility endpoints, mounted at ``RemnawaveClient.system``"""

    async def get_health(self) -> RemnawaveHealth:
        """Runtime health metrics (GET /api/system/health)"""
        envelope: Envelope[RemnawaveHealth] = await self._client.request(
            "GET", "/api/system/health",
            response_type=Envelope[RemnawaveHealth],
        )
        return envelope.response

    async def get_metadata(self) -> RemnawaveMetadata:
        """Panel build/version metadata (GET /api/system/metadata)"""
        envelope: Envelope[RemnawaveMetadata] = await self._client.request(
            "GET", "/api/system/metadata",
            response_type=Envelope[RemnawaveMetadata],
        )
        return envelope.response

    async def get_nodes_metrics(self) -> NodesMetrics:
        """Per-node online and inbound/outbound metrics (GET /api/system/nodes/metrics)"""
        envelope: Envelope[NodesMetrics] = await self._client.request(
            "GET", "/api/system/nodes/metrics",
            response_type=Envelope[NodesMetrics],
        )
        return envelope.response

    async def debug_srr_matcher(
        self,
        response_rules: SrrMatcherResponseRules | dict[str, Any],
    ) -> SrrMatcherResult:
        """Run the subscription response-rules matcher tester"""
        envelope: Envelope[SrrMatcherResult] = await self._client.request(
            "POST", "/api/system/testers/srr-matcher",
            body=pack(response_rules=response_rules),
            response_type=Envelope[SrrMatcherResult],
        )
        return envelope.response

    async def generate_x25519_keypairs(self) -> X25519Keypairs:
        """Generate X25519 key pairs (GET /api/system/tools/x25519/generate)"""
        envelope: Envelope[X25519Keypairs] = await self._client.request(
            "GET", "/api/system/tools/x25519/generate",
            response_type=Envelope[X25519Keypairs],
        )
        return envelope.response

    async def generate_public_key(self) -> PublicKey:
        """Generate a public key (GET /api/keygen)"""
        envelope: Envelope[PublicKey] = await self._client.request(
            "GET", "/api/keygen",
            response_type=Envelope[PublicKey],
        )
        return envelope.response
