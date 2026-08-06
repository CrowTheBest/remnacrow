from typing import Any

from ..enums import HostAlpn, HostMihomoIpVersion, HostSecurityLayer, SubscriptionTemplateType
from .base import Struct


class HostInbound(Struct):
    config_profile_uuid: str | None
    config_profile_inbound_uuid: str | None


class Host(Struct):
    uuid: str
    view_position: int
    remark: str
    address: str
    port: int
    path: str | None
    sni: str | None
    host: str | None
    alpn: HostAlpn | None
    fingerprint: str | None
    is_disabled: bool
    xhttp_extra_params: Any | None
    mux_params: Any | None
    sockopt_params: Any | None
    final_mask: Any | None
    inbound: HostInbound
    server_description: str | None
    vless_route_id: int | None
    pinned_peer_cert_sha256: str | None
    verify_peer_cert_by_name: str | None
    shuffle_host: bool
    mihomo_x25519: bool
    mihomo_ip_version: HostMihomoIpVersion | None
    nodes: list[str]
    xray_json_template_uuid: str | None
    excluded_internal_squads: list[str]
    exclude_from_subscription_types: list[SubscriptionTemplateType]
    security_layer: HostSecurityLayer = HostSecurityLayer.DEFAULT
    tags: list[str] = []
    is_hidden: bool = False
    override_sni_from_address: bool = False
    keep_sni_blank: bool = False
