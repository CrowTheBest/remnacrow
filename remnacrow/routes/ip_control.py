from ..models.common import EventSentResult
from ..models.envelope import Envelope
from ..models.ip_control import (
    FetchUserIpsJobResult,
    FetchUsersIpsJobResult,
    IpControlJob,
)
from .base import BaseRoute


class IpControlRoute(BaseRoute):
    """``/api/ip-control`` endpoints, mounted at ``RemnawaveClient.ip_control``"""

    async def fetch_user_ips(self, uuid: str) -> str:
        """Start collecting the current IP list for one user."""
        envelope: Envelope[IpControlJob] = await self._client.request(
            "POST",
            f"/api/ip-control/fetch-ips/{uuid}",
            response_type=Envelope[IpControlJob],
        )
        return envelope.response.job_id

    async def get_fetch_user_ips_result(self, job_id: str) -> FetchUserIpsJobResult:
        """Read the result/status for ``fetch_user_ips``."""
        envelope: Envelope[FetchUserIpsJobResult] = await self._client.request(
            "GET",
            f"/api/ip-control/fetch-ips/result/{job_id}",
            response_type=Envelope[FetchUserIpsJobResult],
        )
        return envelope.response

    async def drop_connections(
        self,
        *,
        user_uuids: list[str] | None = None,
        ip_addresses: list[str] | None = None,
        node_uuids: list[str] | None = None,
    ) -> bool:
        """Drop connections by user UUIDs or IP addresses.

        If ``node_uuids`` is omitted, the panel targets every connected node.
        """
        if (user_uuids is None) == (ip_addresses is None):
            raise ValueError("pass exactly one of user_uuids or ip_addresses")

        if user_uuids is not None:
            drop_by = {"by": "userUuids", "userUuids": user_uuids}
        else:
            drop_by = {"by": "ipAddresses", "ipAddresses": ip_addresses}

        if node_uuids is None:
            target_nodes = {"target": "allNodes"}
        else:
            target_nodes = {"target": "specificNodes", "nodeUuids": node_uuids}

        envelope: Envelope[EventSentResult] = await self._client.request(
            "POST",
            "/api/ip-control/drop-connections",
            body={"dropBy": drop_by, "targetNodes": target_nodes},
            response_type=Envelope[EventSentResult],
        )
        return envelope.response.event_sent

    async def fetch_users_ips(self, node_uuid: str) -> str:
        """Start collecting IP lists for every user on one node."""
        envelope: Envelope[IpControlJob] = await self._client.request(
            "POST",
            f"/api/ip-control/fetch-users-ips/{node_uuid}",
            response_type=Envelope[IpControlJob],
        )
        return envelope.response.job_id

    async def get_fetch_users_ips_result(self, job_id: str) -> FetchUsersIpsJobResult:
        """Read the result/status for ``fetch_users_ips``."""
        envelope: Envelope[FetchUsersIpsJobResult] = await self._client.request(
            "GET",
            f"/api/ip-control/fetch-users-ips/result/{job_id}",
            response_type=Envelope[FetchUsersIpsJobResult],
        )
        return envelope.response
