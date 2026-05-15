from datetime import datetime

from ..enums import TrafficLimitStrategy, UserStatus
from .base import Struct


# .response.user (or .response.subscriptions[].user) on every subscription read DTO
class SubscriptionUser(Struct):
    short_uuid: str
    days_left: float
    traffic_used: str
    traffic_limit: str
    lifetime_traffic_used: str
    traffic_used_bytes: str
    traffic_limit_bytes: str
    lifetime_traffic_used_bytes: str
    username: str
    expires_at: datetime
    is_active: bool
    user_status: UserStatus
    traffic_limit_strategy: TrafficLimitStrategy


# .response on /api/subscriptions/by-{uuid,short-uuid,username}, item of
# .response.subscriptions[] on /api/subscriptions
class Subscription(Struct):
    is_found: bool
    user: SubscriptionUser
    links: list[str]
    ss_conf_links: dict[str, str]
    subscription_url: str


# .response on /api/subscriptions
class SubscriptionsPage(Struct):
    subscriptions: list[Subscription]
    total: int


# .response on /api/subscriptions/connection-keys/{uuid}
class ConnectionKeys(Struct):
    enabled_keys: list[str]
    hidden_keys: list[str]
    disabled_keys: list[str]


# .response on /api/subscriptions/subpage-config/{shortUuid}
class SubpageConfig(Struct):
    webpage_allowed: bool
    subpage_config_uuid: str | None = None


# item of .response.byParsedApp[] on /api/subscription-request-history/stats
class SubscriptionRequestStatsApp(Struct):
    app: str
    count: int


# item of .response.hourlyRequestStats[] on /api/subscription-request-history/stats
class SubscriptionRequestHourlyStat(Struct):
    date_time: datetime
    request_count: int


# .response on /api/subscription-request-history/stats
class SubscriptionRequestHistoryStats(Struct):
    by_parsed_app: list[SubscriptionRequestStatsApp]
    hourly_request_stats: list[SubscriptionRequestHourlyStat]
