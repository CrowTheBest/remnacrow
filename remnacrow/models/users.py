from datetime import datetime

from .base import Struct
from ..enums import TrafficLimitStrategy, UserStatus


# item of activeInternalSquads[] in UserResponseDto
class Squad(Struct):
    uuid: str
    name: str


# nested userTraffic object in UserResponseDto
class UserTraffic(Struct):
    used_traffic_bytes: int
    lifetime_used_traffic_bytes: int
    online_at: datetime | None
    first_connected_at: datetime | None
    last_connected_node_uuid: str | None


# .response in *UserResponseDto: CreateUser, UpdateUser,
# GetUserBy{Uuid,ShortUuid,Username,Id}; items in GetUserBy{TelegramId,Email,Tag};
# DisableUser, EnableUser, ResetUserTraffic, RevokeUserSubscription
class User(Struct):
    uuid: str
    id: int
    short_uuid: str
    username: str
    expire_at: datetime
    telegram_id: int | None
    email: str | None
    description: str | None
    tag: str | None
    hwid_device_limit: int | None
    external_squad_uuid: str | None
    trojan_password: str
    vless_uuid: str
    ss_password: str
    sub_revoked_at: datetime | None
    last_traffic_reset_at: datetime | None
    created_at: datetime
    updated_at: datetime
    subscription_url: str
    active_internal_squads: list[Squad]
    user_traffic: UserTraffic
    status: UserStatus = UserStatus.ACTIVE
    traffic_limit_bytes: int = 0
    traffic_limit_strategy: TrafficLimitStrategy = TrafficLimitStrategy.NO_RESET
    last_triggered_threshold: int = 0


# GetAllUsersResponseDto.response
class UsersPage(Struct):
    users: list[User]
    total: int


# item of activeSquads[] inside AccessibleNode
class AccessibleSquad(Struct):
    squad_name: str
    active_inbounds: list[str]


# item of activeNodes[] in GetUserAccessibleNodesResponseDto.response
class AccessibleNode(Struct):
    uuid: str
    node_name: str
    country_code: str
    config_profile_uuid: str
    config_profile_name: str
    active_squads: list[AccessibleSquad]


# GetUserAccessibleNodesResponseDto.response
class AccessibleNodesResult(Struct):
    user_uuid: str
    active_nodes: list[AccessibleNode]


# item of records[] in GetUserSubscriptionRequestHistoryResponseDto.response
class SubscriptionRequestRecord(Struct):
    id: int
    user_uuid: str
    request_at: datetime
    request_ip: str | None
    user_agent: str | None


# GetUserSubscriptionRequestHistoryResponseDto.response
class SubscriptionRequestHistory(Struct):
    total: int
    records: list[SubscriptionRequestRecord]


# ResolveUserResponseDto.response
class ResolvedUser(Struct):
    uuid: str
    username: str
    id: int
    short_uuid: str
