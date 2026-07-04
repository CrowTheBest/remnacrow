from datetime import datetime

from .base import Struct


# items of .response.devices[] in most *HwidDevice*ResponseDto schemas
class HwidDevice(Struct):
    hwid: str
    platform: str | None
    os_version: str | None
    device_model: str | None
    user_agent: str | None
    created_at: datetime
    updated_at: datetime
    user_uuid: str | None = None
    user_id: int | None = None


# .response in GetAllHwidDevicesResponseDto, CreateUserHwidDeviceResponseDto,
# DeleteUserHwidDeviceResponseDto, DeleteAllUserHwidDevicesResponseDto,
# GetUserHwidDevicesResponseDto
class HwidDevicesPage(Struct):
    devices: list[HwidDevice]
    total: int


# item of .response.byPlatform[] in GetHwidDevicesStatsResponseDto
class HwidPlatformCount(Struct):
    platform: str
    count: int


# item of .response.byApp[] in GetHwidDevicesStatsResponseDto
class HwidAppCount(Struct):
    app: str
    count: int


# .response.stats in GetHwidDevicesStatsResponseDto
class HwidGlobalStats(Struct):
    total_unique_devices: int
    total_hwid_devices: int
    average_hwid_devices_per_user: float


# .response in GetHwidDevicesStatsResponseDto
class HwidDevicesStats(Struct):
    by_platform: list[HwidPlatformCount]
    by_app: list[HwidAppCount]
    stats: HwidGlobalStats


# item of .response.users[] in GetTopUsersByHwidDevicesResponseDto
class HwidTopUser(Struct):
    username: str
    devices_count: int
    id: int | None = None
    user_uuid: str | None = None
    user_id: int | None = None

    def __post_init__(self) -> None:
        if self.user_id is None and self.id is not None:
            self.user_id = self.id
        elif self.id is None and self.user_id is not None:
            self.id = self.user_id


# .response in GetTopUsersByHwidDevicesResponseDto
class HwidTopUsersPage(Struct):
    users: list[HwidTopUser]
    total: int
