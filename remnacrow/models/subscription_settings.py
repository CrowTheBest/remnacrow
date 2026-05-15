from datetime import datetime
from typing import Any

from .base import Struct


# .hwidSettings on /api/subscription-settings (same shape as on external squads,
# but kept module-local to avoid cross-module coupling)
class SubscriptionHwidSettings(Struct):
    enabled: bool
    fallback_device_limit: int
    max_devices_announce: str | None = None


# .response on /api/subscription-settings (GET, PATCH).
# ``custom_remarks`` is left as a raw dict because the panel uses PascalCase
# keys ``HWIDMaxDevicesExceeded`` / ``HWIDNotSupported`` that don't round-trip
# through ``rename="camel"``.
# ``response_rules`` is a complex deeply nested SRR config — kept as raw dict
# pass-through.
class SubscriptionSettings(Struct):
    uuid: str
    profile_title: str
    support_link: str
    profile_update_interval: int
    is_profile_webpage_url_enabled: bool
    serve_json_at_base_subscription: bool
    is_show_custom_remarks: bool
    custom_remarks: dict[str, list[str]]
    randomize_hosts: bool
    created_at: datetime
    updated_at: datetime
    happ_announce: str | None = None
    happ_routing: str | None = None
    custom_response_headers: dict[str, str] | None = None
    response_rules: dict[str, Any] | None = None
    hwid_settings: SubscriptionHwidSettings | None = None
