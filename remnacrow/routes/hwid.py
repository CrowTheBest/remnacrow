from typing import Any

from ..models.envelope import Envelope
from ..models.filters import Filter, Sort
from ..models.hwid import HwidDevicesPage, HwidDevicesStats, HwidTopUsersPage
from .base import BaseRoute, build_list_params, pack


class HwidRoute(BaseRoute):
    """``/api/hwid`` endpoints, mounted at ``RemnawaveClient.hwid``"""

    async def get_devices(
        self,
        *,
        size: int = 25,
        start: int = 0,
        filters: list[Filter] | None = None,
        sort: list[Sort] | None = None,
    ) -> HwidDevicesPage:
        """
        Paginated list of every HWID device across all users
        (GET /api/hwid/devices)

        Filter/sort params mirror the admin UI's TanStack-table format and
        are not in the OpenAPI spec. Each value is JSON-encoded and sent as
        a query string.

        Supported filter modes (see :class:`~remnacrow.models.FilterMode`):
        ``contains``, ``startsWith``, ``endsWith``, ``equals``.

        Use :class:`~remnacrow.models.HwidField` for autocomplete on column
        names: ``hwid``, ``userUuid``, ``platform``, ``osVersion``,
        ``deviceModel``, ``userAgent``, ``createdAt``, ``updatedAt``.

        :param size: page size; defaults to 25 to match the panel default
        :param start: offset from the start of the device list
        :param filters: list of :class:`~remnacrow.models.Filter` constraints
        :param sort: ordered list of :class:`~remnacrow.models.Sort` keys
        :return: :class:`~remnacrow.models.HwidDevicesPage` with ``devices``
            (current page) and ``total`` (count of devices matching the
            query — panel-wide when no filter is applied)
        """
        envelope: Envelope[HwidDevicesPage] = await self._client.request(
            "GET",
            "/api/hwid/devices",
            params=build_list_params(size, start, filters, sort),
            response_type=Envelope[HwidDevicesPage],
        )
        return envelope.response

    async def create_device(
        self,
        hwid: str,
        user_uuid: str,
        *,
        platform: str | None = None,
        os_version: str | None = None,
        device_model: str | None = None,
        user_agent: str | None = None,
    ) -> HwidDevicesPage:
        """
        Register a new HWID device for a user (POST /api/hwid/devices)

        :param hwid: device hardware id
        :param user_uuid: uuid of the user this device belongs to
        :param platform: platform string (e.g. ``"iOS"``, ``"Android"``, ``"Windows"``)
        :param os_version: OS version string
        :param device_model: human-readable device model
        :param user_agent: client app user-agent string
        :return: :class:`~remnacrow.models.HwidDevicesPage` with the user's
            full device list after the new entry was added
        """
        body = pack(
            hwid=hwid,
            user_uuid=user_uuid,
            platform=platform,
            os_version=os_version,
            device_model=device_model,
            user_agent=user_agent,
        )
        envelope: Envelope[HwidDevicesPage] = await self._client.request(
            "POST",
            "/api/hwid/devices",
            body=body,
            response_type=Envelope[HwidDevicesPage],
        )
        return envelope.response

    async def delete_device(self, user_uuid: str, hwid: str) -> HwidDevicesPage:
        """
        Delete one HWID device (POST /api/hwid/devices/delete)

        :param user_uuid: uuid of the user that owns the device
        :param hwid: hardware id of the device to delete
        :return: :class:`~remnacrow.models.HwidDevicesPage` with the user's
            remaining devices after deletion
        """
        body = pack(user_uuid=user_uuid, hwid=hwid)
        envelope: Envelope[HwidDevicesPage] = await self._client.request(
            "POST",
            "/api/hwid/devices/delete",
            body=body,
            response_type=Envelope[HwidDevicesPage],
        )
        return envelope.response

    async def delete_all_devices(self, user_uuid: str) -> HwidDevicesPage:
        """
        Delete every HWID device that belongs to a user
        (POST /api/hwid/devices/delete-all)

        :param user_uuid: uuid of the user whose devices to wipe
        :return: :class:`~remnacrow.models.HwidDevicesPage` — typically with
            an empty ``devices`` list and ``total=0``
        """
        body = pack(user_uuid=user_uuid)
        envelope: Envelope[HwidDevicesPage] = await self._client.request(
            "POST",
            "/api/hwid/devices/delete-all",
            body=body,
            response_type=Envelope[HwidDevicesPage],
        )
        return envelope.response

    async def get_devices_stats(self) -> HwidDevicesStats:
        """
        Global HWID device statistics (GET /api/hwid/devices/stats)

        Aggregates across every user: counts per platform, counts per
        connected app, and overall totals + average devices per user.

        :return: :class:`~remnacrow.models.HwidDevicesStats` with
            ``by_platform``, ``by_app``, and ``stats``
        """
        envelope: Envelope[HwidDevicesStats] = await self._client.request(
            "GET",
            "/api/hwid/devices/stats",
            response_type=Envelope[HwidDevicesStats],
        )
        return envelope.response

    async def get_top_users(
        self, *, size: int = 25, start: int = 0
    ) -> HwidTopUsersPage:
        """
        Top users sorted by number of registered HWID devices
        (GET /api/hwid/devices/top-users)

        :param size: page size; defaults to 25 to match the panel default
        :param start: offset from the start of the ranking
        :return: :class:`~remnacrow.models.HwidTopUsersPage` with the
            current page of :class:`~remnacrow.models.HwidTopUser` entries
            plus ``total``
        """
        params: dict[str, Any] = {"size": size, "start": start}
        envelope: Envelope[HwidTopUsersPage] = await self._client.request(
            "GET",
            "/api/hwid/devices/top-users",
            params=params,
            response_type=Envelope[HwidTopUsersPage],
        )
        return envelope.response

    async def get_user_devices(self, user_uuid: str) -> HwidDevicesPage:
        """
        All HWID devices that belong to a specific user
        (GET /api/hwid/devices/{userUuid})

        :param user_uuid: uuid of the user
        :return: :class:`~remnacrow.models.HwidDevicesPage` with the user's
            devices and total count
        """
        envelope: Envelope[HwidDevicesPage] = await self._client.request(
            "GET",
            f"/api/hwid/devices/{user_uuid}",
            response_type=Envelope[HwidDevicesPage],
        )
        return envelope.response
