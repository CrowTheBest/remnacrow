from datetime import datetime

from .base import Struct


class InfraBillingHistorySummary(Struct):
    total_amount: float
    total_bills: int


class InfraBillingNodeDetails(Struct):
    node_uuid: str
    country_code: str


class InfraProviderBillingNodeSummary(Struct):
    name: str
    details: InfraBillingNodeDetails | None


class InfraProvider(Struct):
    uuid: str
    name: str
    favicon_link: str | None
    login_url: str | None
    created_at: datetime
    updated_at: datetime
    billing_history: InfraBillingHistorySummary
    billing_nodes: list[InfraProviderBillingNodeSummary]


class InfraProvidersPage(Struct):
    total: int
    providers: list[InfraProvider]


class InfraBillingHistoryProvider(Struct):
    uuid: str
    name: str
    favicon_link: str | None


class InfraBillingHistoryRecord(Struct):
    uuid: str
    provider_uuid: str
    amount: float
    billed_at: datetime
    provider: InfraBillingHistoryProvider


class InfraBillingHistoryPage(Struct):
    records: list[InfraBillingHistoryRecord]
    total: int


class InfraBillingNodeProvider(Struct):
    uuid: str
    name: str
    login_url: str | None
    favicon_link: str | None


class InfraBillingNodeRef(Struct):
    uuid: str
    name: str
    country_code: str


class InfraBillingNode(Struct):
    uuid: str
    node_uuid: str | None
    name: str | None
    provider_uuid: str
    provider: InfraBillingNodeProvider
    node: InfraBillingNodeRef | None
    next_billing_at: datetime
    created_at: datetime
    updated_at: datetime


class InfraBillingStats(Struct):
    upcoming_nodes_count: int
    current_month_payments: float
    total_spent: float


class InfraBillingNodesPage(Struct):
    total_billing_nodes: int
    billing_nodes: list[InfraBillingNode]
    available_billing_nodes: list[InfraBillingNodeRef]
    total_available_billing_nodes: int
    stats: InfraBillingStats
