from datetime import datetime
from typing import Any

from .base import Struct


class NodePlugin(Struct):
    uuid: str
    view_position: int
    name: str
    plugin_config: Any | None


class NodePluginsPage(Struct):
    total: int
    node_plugins: list[NodePlugin]


class TorrentBlockerReportUser(Struct):
    uuid: str
    username: str


class TorrentBlockerReportNode(Struct):
    uuid: str
    name: str
    country_code: str


class TorrentBlockerActionReport(Struct):
    blocked: bool
    ip: str
    block_duration: float
    will_unblock_at: datetime
    user_id: str
    processed_at: datetime


class TorrentBlockerXrayReport(Struct):
    email: str | None
    level: float | None
    protocol: str | None
    network: str
    source: str | None
    destination: str
    route_target: str | None
    original_target: str | None
    inbound_tag: str | None
    inbound_name: str | None
    inbound_local: str | None
    outbound_tag: str | None
    ts: float


class TorrentBlockerReportPayload(Struct):
    action_report: TorrentBlockerActionReport
    xray_report: TorrentBlockerXrayReport


class TorrentBlockerReport(Struct):
    id: int
    user_id: int
    node_id: int
    user: TorrentBlockerReportUser
    node: TorrentBlockerReportNode
    report: TorrentBlockerReportPayload
    created_at: datetime


class TorrentBlockerReportsPage(Struct):
    records: list[TorrentBlockerReport]
    total: int
