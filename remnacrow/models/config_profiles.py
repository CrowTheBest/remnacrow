from datetime import datetime
from typing import Any

from .base import Struct


class ConfigProfileInbound(Struct):
    uuid: str
    profile_uuid: str
    tag: str
    type: str
    network: str | None
    security: str | None
    port: float | None
    raw_inbound: Any | None


class ConfigProfileInboundWithSquads(Struct):
    uuid: str
    profile_uuid: str
    tag: str
    type: str
    network: str | None
    security: str | None
    port: float | None
    raw_inbound: Any | None
    active_squads: list[str]


class ConfigProfileNode(Struct):
    uuid: str
    name: str
    country_code: str


class ConfigProfile(Struct):
    uuid: str
    view_position: int
    name: str
    config: Any
    inbounds: list[ConfigProfileInbound]
    nodes: list[ConfigProfileNode]
    created_at: datetime
    updated_at: datetime


class ConfigProfilesPage(Struct):
    total: int
    config_profiles: list[ConfigProfile]


class ConfigProfileInboundsPage(Struct):
    total: int
    inbounds: list[ConfigProfileInboundWithSquads]
