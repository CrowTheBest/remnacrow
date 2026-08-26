from ..models.common import DeletedResult
from ..models.envelope import Envelope
from ..models.infra_billing import (
    InfraBillingHistoryPage,
    InfraBillingNodesPage,
    InfraProvider,
    InfraProvidersPage,
)
from .base import BaseRoute, pack


class InfraBillingRoute(BaseRoute):
    """``/api/infra-billing`` endpoints."""

    async def get_providers(self) -> InfraProvidersPage:
        envelope: Envelope[InfraProvidersPage] = await self._client.request(
            "GET",
            "/api/infra-billing/providers",
            response_type=Envelope[InfraProvidersPage],
        )
        return envelope.response

    async def create_provider(
        self,
        name: str,
        *,
        favicon_link: str | None = None,
        login_url: str | None = None,
    ) -> InfraProvider:
        body = pack(name=name, favicon_link=favicon_link, login_url=login_url)
        envelope: Envelope[InfraProvider] = await self._client.request(
            "POST",
            "/api/infra-billing/providers",
            body=body,
            response_type=Envelope[InfraProvider],
        )
        return envelope.response

    async def update_provider(
        self,
        uuid: str,
        *,
        name: str | None = None,
        favicon_link: str | None = None,
        login_url: str | None = None,
    ) -> InfraProvider:
        body = pack(uuid=uuid, name=name, favicon_link=favicon_link, login_url=login_url)
        envelope: Envelope[InfraProvider] = await self._client.request(
            "PATCH",
            "/api/infra-billing/providers",
            body=body,
            response_type=Envelope[InfraProvider],
        )
        return envelope.response

    async def get_provider_by_uuid(self, uuid: str) -> InfraProvider:
        envelope: Envelope[InfraProvider] = await self._client.request(
            "GET",
            f"/api/infra-billing/providers/{uuid}",
            response_type=Envelope[InfraProvider],
        )
        return envelope.response

    async def delete_provider(self, uuid: str) -> bool:
        envelope: Envelope[DeletedResult] = await self._client.request(
            "DELETE",
            f"/api/infra-billing/providers/{uuid}",
            response_type=Envelope[DeletedResult],
        )
        return envelope.response.is_deleted

    async def create_history_record(
        self,
        provider_uuid: str,
        amount: float,
        billed_at: str,
    ) -> InfraBillingHistoryPage:
        body = {"providerUuid": provider_uuid, "amount": amount, "billedAt": billed_at}
        envelope: Envelope[InfraBillingHistoryPage] = await self._client.request(
            "POST",
            "/api/infra-billing/history",
            body=body,
            response_type=Envelope[InfraBillingHistoryPage],
        )
        return envelope.response

    async def get_history_records(self) -> InfraBillingHistoryPage:
        envelope: Envelope[InfraBillingHistoryPage] = await self._client.request(
            "GET",
            "/api/infra-billing/history",
            response_type=Envelope[InfraBillingHistoryPage],
        )
        return envelope.response

    async def delete_history_record(self, uuid: str) -> bool:
        envelope: Envelope[DeletedResult] = await self._client.request(
            "DELETE",
            f"/api/infra-billing/history/{uuid}",
            response_type=Envelope[DeletedResult],
        )
        return envelope.response.is_deleted

    async def get_nodes(self) -> InfraBillingNodesPage:
        envelope: Envelope[InfraBillingNodesPage] = await self._client.request(
            "GET",
            "/api/infra-billing/nodes",
            response_type=Envelope[InfraBillingNodesPage],
        )
        return envelope.response

    async def update_nodes(
        self,
        uuids: list[str],
        next_billing_at: str,
    ) -> InfraBillingNodesPage:
        body = {"uuids": uuids, "nextBillingAt": next_billing_at}
        envelope: Envelope[InfraBillingNodesPage] = await self._client.request(
            "PATCH",
            "/api/infra-billing/nodes",
            body=body,
            response_type=Envelope[InfraBillingNodesPage],
        )
        return envelope.response

    async def create_node(
        self,
        provider_uuid: str,
        next_billing_at: str,
        *,
        node_uuid: str | None = None,
        name: str | None = None,
    ) -> InfraBillingNodesPage:
        body = {
            "providerUuid": provider_uuid,
            "nodeUuid": node_uuid,
            "name": name,
            "nextBillingAt": next_billing_at,
        }
        envelope: Envelope[InfraBillingNodesPage] = await self._client.request(
            "POST",
            "/api/infra-billing/nodes",
            body=body,
            response_type=Envelope[InfraBillingNodesPage],
        )
        return envelope.response

    async def delete_node(self, uuid: str) -> bool:
        envelope: Envelope[DeletedResult] = await self._client.request(
            "DELETE",
            f"/api/infra-billing/nodes/{uuid}",
            response_type=Envelope[DeletedResult],
        )
        return envelope.response.is_deleted
