from datetime import datetime
from typing import Any

from .base import Struct


# item of .response.configProfile.activeInbounds[] on every node payload
class NodeInbound(Struct):
    uuid: str
    profile_uuid: str
    tag: str
    type: str
    network: str | None = None
    security: str | None = None
    port: float | None = None
    raw_inbound: Any | None = None


# .response.configProfile on every node payload
class NodeConfigProfile(Struct):
    active_config_profile_uuid: str | None = None
    active_inbounds: list[NodeInbound] = []


# .response.provider on every node payload
class NodeProvider(Struct):
    uuid: str
    name: str
    created_at: datetime
    updated_at: datetime
    favicon_link: str | None = None
    login_url: str | None = None


# .response.system.info on a connected node
class NodeSystemInfo(Struct):
    arch: str
    cpus: int
    cpu_model: str
    memory_total: float
    hostname: str
    platform: str
    release: str
    type: str
    version: str
    network_interfaces: list[str]


# .response.system.stats.interface on a connected node
class NodeNetworkInterface(Struct):
    interface: str
    rx_bytes_per_sec: float
    tx_bytes_per_sec: float
    rx_total: float
    tx_total: float


# .response.system.stats on a connected node
class NodeSystemStats(Struct):
    memory_free: float
    memory_used: float
    uptime: float
    load_avg: list[float]
    interface: NodeNetworkInterface | None = None


# .response.system on a connected node — None when the node is offline
class NodeSystem(Struct):
    info: NodeSystemInfo
    stats: NodeSystemStats


# .response.versions on a connected node — None when the node is offline
class NodeVersions(Struct):
    xray: str
    node: str


# .response on Create/Get/Update/Disable/Enable/ResetTraffic node response DTOs,
# and item of .response[] on GetAll/Reorder response DTOs
class Node(Struct):
    uuid: str
    name: str
    address: str
    is_connected: bool
    is_disabled: bool
    is_connecting: bool
    is_traffic_tracking_active: bool
    view_position: int
    country_code: str
    consumption_multiplier: float
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    config_profile: NodeConfigProfile
    xray_uptime: float
    users_online: int
    port: int | None = None
    last_status_change: datetime | None = None
    last_status_message: str | None = None
    traffic_reset_day: int | None = None
    traffic_limit_bytes: float | None = None
    traffic_used_bytes: float | None = None
    notify_percent: int | None = None
    provider_uuid: str | None = None
    provider: NodeProvider | None = None
    active_plugin_uuid: str | None = None
    system: NodeSystem | None = None
    versions: NodeVersions | None = None
