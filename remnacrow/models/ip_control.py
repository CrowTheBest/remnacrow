from .base import Struct


class IpControlJob(Struct):
    job_id: str


class IpControlProgress(Struct):
    total: float
    completed: float
    percent: float


class IpControlSeenIp(Struct):
    ip: str
    last_seen: str


class IpControlNodeIps(Struct):
    node_uuid: str
    node_name: str
    country_code: str
    ips: list[IpControlSeenIp]


class FetchUserIpsResult(Struct):
    success: bool
    nodes: list[IpControlNodeIps]
    user_uuid: str | None = None
    user_id: str | int | None = None


class FetchUserIpsJobResult(Struct):
    is_completed: bool
    is_failed: bool
    result: FetchUserIpsResult | None
    progress: IpControlProgress | None = None


class IpControlUserIps(Struct):
    ips: list[IpControlSeenIp]
    user_id: str | int | None = None
    user_uuid: str | None = None


class FetchUsersIpsResult(Struct):
    success: bool
    node_uuid: str
    users: list[IpControlUserIps]


class FetchUsersIpsJobResult(Struct):
    is_completed: bool
    is_failed: bool
    result: FetchUsersIpsResult | None
