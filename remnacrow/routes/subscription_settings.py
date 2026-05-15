from typing import Any

from ..models.envelope import Envelope
from ..models.subscription_settings import SubscriptionSettings
from .base import BaseRoute, pack


class SubscriptionSettingsRoute(BaseRoute):
    """``/api/subscription-settings`` singleton, mounted at
    ``RemnawaveClient.subscription_settings``"""

    async def get_settings(self) -> SubscriptionSettings:
        """
        Fetch the panel-wide subscription settings
        (GET /api/subscription-settings)

        :return: :class:`~remnacrow.models.SubscriptionSettings` — the
            singleton config row
        """
        envelope: Envelope[SubscriptionSettings] = await self._client.request(
            "GET", "/api/subscription-settings",
            response_type=Envelope[SubscriptionSettings],
        )
        return envelope.response

    async def update_settings(
        self,
        uuid: str,
        *,
        profile_title: str | None = None,
        support_link: str | None = None,
        profile_update_interval: int | None = None,
        is_profile_webpage_url_enabled: bool | None = None,
        serve_json_at_base_subscription: bool | None = None,
        happ_announce: str | None = None,
        happ_routing: str | None = None,
        is_show_custom_remarks: bool | None = None,
        custom_remarks: dict[str, list[str]] | None = None,
        custom_response_headers: dict[str, str] | None = None,
        randomize_hosts: bool | None = None,
        response_rules: dict[str, Any] | None = None,
        hwid_settings: dict[str, Any] | None = None,
    ) -> SubscriptionSettings:
        """
        Patch the panel-wide subscription settings
        (PATCH /api/subscription-settings)

        Only the kwargs you pass are forwarded; ``None`` values are
        stripped. Complex sub-objects (``custom_remarks``, ``response_rules``,
        ``hwid_settings``) are accepted as raw dicts because their wire
        format mixes camelCase and PascalCase keys (the panel's SRR config
        and ``HWIDMaxDevicesExceeded`` quirks don't round-trip through
        ``rename="camel"``).

        :param uuid: uuid of the settings row (always the singleton)
        :param profile_title: new title shown in the subscription profile
        :param support_link: new support URL surfaced to clients
        :param profile_update_interval: new auto-refresh interval (hours)
        :param is_profile_webpage_url_enabled: toggle the hosted webpage URL
        :param serve_json_at_base_subscription: serve XRAY_JSON at the bare
            ``/sub/{shortUuid}`` route
        :param happ_announce: Happ-client announcement string (max 200)
        :param happ_routing: Happ-client routing string
        :param is_show_custom_remarks: show per-state remarks in subscription
        :param custom_remarks: per-user-state remark templates with keys
            ``expiredUsers``, ``limitedUsers``, ``disabledUsers``,
            ``emptyHosts``, ``HWIDMaxDevicesExceeded``, ``HWIDNotSupported``
            (note the PascalCase prefix on the two HWID keys)
        :param custom_response_headers: header name → value mapping appended
            to subscription HTTP responses
        :param randomize_hosts: shuffle host order on each subscription render
        :param response_rules: opaque SRR config — pass through the dict as
            the panel UI exports it
        :param hwid_settings: ``{enabled, fallbackDeviceLimit, maxDevicesAnnounce}``
        :return: the updated :class:`~remnacrow.models.SubscriptionSettings`
        """
        body = pack(
            uuid=uuid,
            profile_title=profile_title, support_link=support_link,
            profile_update_interval=profile_update_interval,
            is_profile_webpage_url_enabled=is_profile_webpage_url_enabled,
            serve_json_at_base_subscription=serve_json_at_base_subscription,
            happ_announce=happ_announce, happ_routing=happ_routing,
            is_show_custom_remarks=is_show_custom_remarks,
            custom_response_headers=custom_response_headers,
            randomize_hosts=randomize_hosts,
            response_rules=response_rules, hwid_settings=hwid_settings,
        )
        if custom_remarks is not None:
            body["customRemarks"] = custom_remarks

        envelope: Envelope[SubscriptionSettings] = await self._client.request(
            "PATCH", "/api/subscription-settings",
            body=body, response_type=Envelope[SubscriptionSettings],
        )
        return envelope.response
