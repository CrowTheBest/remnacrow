import enum


class UserStatus(enum.StrEnum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    LIMITED = "LIMITED"
    EXPIRED = "EXPIRED"


class TrafficLimitStrategy(enum.StrEnum):
    NO_RESET = "NO_RESET"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    MONTH_ROLLING = "MONTH_ROLLING"


class FilterMode(enum.StrEnum):
    """Filter modes accepted by the panel for ``UsersRoute.get_users``"""
    CONTAINS = "contains"
    STARTS_WITH = "startsWith"
    ENDS_WITH = "endsWith"
    EQUALS = "equals"


class UserField(enum.StrEnum):
    """Column names of the users table — used as ``Filter.field`` / ``Sort.field``

    Includes nested fields (``userTraffic.*``) which use dotted paths on the wire.
    """
    USERNAME = "username"
    ID = "id"
    UUID = "uuid"
    SHORT_UUID = "shortUuid"
    STATUS = "status"
    TAG = "tag"
    DESCRIPTION = "description"
    EMAIL = "email"
    TELEGRAM_ID = "telegramId"
    EXPIRE_AT = "expireAt"
    CREATED_AT = "createdAt"
    SUB_REVOKED_AT = "subRevokedAt"
    LAST_TRAFFIC_RESET_AT = "lastTrafficResetAt"
    USED_TRAFFIC_BYTES = "usedTrafficBytes"
    LIFETIME_USED_TRAFFIC_BYTES = "userTraffic.lifetimeUsedTrafficBytes"
    ONLINE_AT = "userTraffic.onlineAt"
    FIRST_CONNECTED_AT = "userTraffic.firstConnectedAt"
    NODE_NAME = "nodeName"  # actually last-connected node uuid, despite the name
    ACTIVE_INTERNAL_SQUADS = "activeInternalSquads"
    EXTERNAL_SQUAD_UUID = "externalSquadUuid"
    HWID_DEVICE_LIMIT = "hwidDeviceLimit"
    VLESS_UUID = "vlessUuid"
    TROJAN_PASSWORD = "trojanPassword"
