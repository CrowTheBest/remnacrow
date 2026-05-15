from datetime import datetime
from typing import Any

from ..enums import SubscriptionTemplateType
from .base import Struct


# .inbounds[] item on every internal-squad payload
# (same shape as :class:`~remnacrow.models.NodeInbound`)
class SquadInbound(Struct):
    uuid: str
    profile_uuid: str
    tag: str
    type: str
    network: str | None = None
    security: str | None = None
    port: float | None = None
    raw_inbound: Any | None = None


# .info on every internal-squad payload
class InternalSquadInfo(Struct):
    members_count: int
    inbounds_count: int


# .response on Create/Update/Get internal-squad responses, item of
# .response.internalSquads[] on Get/Reorder list responses
class InternalSquad(Struct):
    uuid: str
    view_position: int
    name: str
    info: InternalSquadInfo
    inbounds: list[SquadInbound]
    created_at: datetime
    updated_at: datetime


# .response on Get/Reorder internal-squad list responses
class InternalSquadsPage(Struct):
    total: int
    internal_squads: list[InternalSquad]


# .response.accessibleNodes[] item on /api/internal-squads/{uuid}/accessible-nodes
class SquadAccessibleNode(Struct):
    uuid: str
    node_name: str
    country_code: str
    config_profile_uuid: str
    config_profile_name: str
    active_inbounds: list[str]


# .response on /api/internal-squads/{uuid}/accessible-nodes
class SquadAccessibleNodesResult(Struct):
    squad_uuid: str
    accessible_nodes: list[SquadAccessibleNode]


# .info on every external-squad payload
class ExternalSquadInfo(Struct):
    members_count: int


# .templates[] item on every external-squad payload
class ExternalSquadTemplate(Struct):
    template_uuid: str
    template_type: SubscriptionTemplateType


# .subscriptionSettings on an external-squad payload
class ExternalSquadSubscriptionSettings(Struct):
    profile_title: str
    support_link: str
    profile_update_interval: int
    is_profile_webpage_url_enabled: bool
    serve_json_at_base_subscription: bool
    is_show_custom_remarks: bool
    randomize_hosts: bool
    happ_announce: str | None = None
    happ_routing: str | None = None


# .hostOverrides on an external-squad payload
class ExternalSquadHostOverrides(Struct):
    server_description: str | None = None
    vless_route_id: int | None = None


# .hwidSettings on an external-squad payload
class ExternalSquadHwidSettings(Struct):
    enabled: bool
    fallback_device_limit: int
    max_devices_announce: str | None = None


# .response on Create/Update/Get external-squad responses, item of
# .response.externalSquads[] on Get/Reorder list responses.
# `custom_remarks` is left as a raw dict because the panel uses
# PascalCase keys (``HWIDMaxDevicesExceeded``, ``HWIDNotSupported``) that
# don't round-trip through ``rename="camel"``.
class ExternalSquad(Struct):
    uuid: str
    view_position: int
    name: str
    info: ExternalSquadInfo
    templates: list[ExternalSquadTemplate]
    created_at: datetime
    updated_at: datetime
    subscription_settings: ExternalSquadSubscriptionSettings | None = None
    host_overrides: ExternalSquadHostOverrides | None = None
    response_headers: dict[str, str] | None = None
    hwid_settings: ExternalSquadHwidSettings | None = None
    custom_remarks: dict[str, list[str]] | None = None
    subpage_config_uuid: str | None = None


# .response on Get/Reorder external-squad list responses
class ExternalSquadsPage(Struct):
    total: int
    external_squads: list[ExternalSquad]
