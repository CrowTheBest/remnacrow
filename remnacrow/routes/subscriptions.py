from typing import Any

from ..models.envelope import Envelope
from ..models.subscriptions import (
    ConnectionKeys,
    SubpageConfig,
    Subscription,
    SubscriptionRequestHistoryStats,
    SubscriptionsPage,
)
from ..models.users import SubscriptionRequestHistory
from .base import BaseRoute


class SubscriptionsRoute(BaseRoute):
    """``/api/subscriptions`` admin reads and public ``/api/sub`` helpers.

    These are *admin-facing* endpoints — i.e. the same panel UI that lists
    users also lets you peek at each user's rendered subscription metadata.
    """

    async def get_subscriptions(
        self, *, size: int = 25, start: int = 0
    ) -> SubscriptionsPage:
        """
        Paginated list of every user's subscription metadata
        (GET /api/subscriptions)

        :param size: page size; defaults to 25 to match the panel default
        :param start: offset from the start of the user list
        :return: :class:`~remnacrow.models.SubscriptionsPage` with ``total``
            and ``subscriptions`` for the current page
        """
        params: dict[str, Any] = {"size": size, "start": start}
        envelope: Envelope[SubscriptionsPage] = await self._client.request(
            "GET", "/api/subscriptions",
            params=params, response_type=Envelope[SubscriptionsPage],
        )
        return envelope.response

    async def get_subscription_by_uuid(self, uuid: str) -> Subscription:
        """
        Fetch one user's subscription by user uuid
        (GET /api/subscriptions/by-uuid/{uuid})

        :param uuid: uuid of the user
        :return: matching :class:`~remnacrow.models.Subscription`
        """
        envelope: Envelope[Subscription] = await self._client.request(
            "GET", f"/api/subscriptions/by-uuid/{uuid}",
            response_type=Envelope[Subscription],
        )
        return envelope.response

    async def get_subscription_by_username(self, username: str) -> Subscription:
        """
        Fetch one user's subscription by username
        (GET /api/subscriptions/by-username/{username})

        :param username: username of the user
        :return: matching :class:`~remnacrow.models.Subscription`
        """
        envelope: Envelope[Subscription] = await self._client.request(
            "GET", f"/api/subscriptions/by-username/{username}",
            response_type=Envelope[Subscription],
        )
        return envelope.response

    async def get_subscription_by_short_uuid(self, short_uuid: str) -> Subscription:
        """
        Fetch one user's subscription by ``short_uuid`` — same value used in
        the public sub URL (GET /api/subscriptions/by-short-uuid/{shortUuid})

        :param short_uuid: short uuid of the user
        :return: matching :class:`~remnacrow.models.Subscription`
        """
        envelope: Envelope[Subscription] = await self._client.request(
            "GET", f"/api/subscriptions/by-short-uuid/{short_uuid}",
            response_type=Envelope[Subscription],
        )
        return envelope.response

    async def get_public_subscription_info(self, short_uuid: str) -> Subscription:
        """
        Fetch public subscription info by short uuid
        (GET /api/sub/{shortUuid}/info)
        """
        envelope: Envelope[Subscription] = await self._client.request(
            "GET",
            f"/api/sub/{short_uuid}/info",
            response_type=Envelope[Subscription],
        )
        return envelope.response

    async def get_public_subscription(self, short_uuid: str) -> str:
        """Fetch the public subscription payload as text (GET /api/sub/{shortUuid})"""
        return await self._client.request_text("GET", f"/api/sub/{short_uuid}")

    async def get_public_subscription_by_client_type(
        self,
        short_uuid: str,
        client_type: str,
    ) -> str:
        """
        Fetch the public subscription payload for one client type
        (GET /api/sub/{shortUuid}/{clientType}).
        """
        return await self._client.request_text(
            "GET",
            f"/api/sub/{short_uuid}/{client_type}",
        )

    async def get_raw_subscription_by_short_uuid(
        self,
        short_uuid: str,
        *,
        with_disabled_hosts: bool | None = None,
    ) -> dict[str, Any]:
        """
        Fetch the raw, untemplated subscription payload by ``short_uuid``
        (GET /api/subscriptions/by-short-uuid/{shortUuid}/raw)

        This dumps the full user + host list the panel would normally feed
        through a subscription template. Returned as a plain ``dict`` so
        consumers can pluck the fields they need without a heavy model.

        :param short_uuid: short uuid of the user
        :param with_disabled_hosts: if ``True``, include hosts that are
            currently disabled
        :return: raw response payload (``response`` envelope unwrapped)
        """
        params: dict[str, Any] = {}
        if with_disabled_hosts is not None:
            params["withDisabledHosts"] = "true" if with_disabled_hosts else "false"

        data = await self._client.request(
            "GET", f"/api/subscriptions/by-short-uuid/{short_uuid}/raw",
            params=params or None, response_type=dict,
        )
        return data["response"]

    async def get_connection_keys(self, uuid: str) -> ConnectionKeys:
        """
        Per-protocol connection-key lists for one user
        (GET /api/subscriptions/connection-keys/{uuid})

        :param uuid: uuid of the user
        :return: :class:`~remnacrow.models.ConnectionKeys` with
            ``enabled_keys`` / ``hidden_keys`` / ``disabled_keys``
        """
        envelope: Envelope[ConnectionKeys] = await self._client.request(
            "GET", f"/api/subscriptions/connection-keys/{uuid}",
            response_type=Envelope[ConnectionKeys],
        )
        return envelope.response

    async def get_subpage_config(
        self, short_uuid: str, *, request_headers: dict[str, str],
    ) -> SubpageConfig:
        """
        Resolve which subpage-config a given subscription request would hit
        (GET /api/subscriptions/subpage-config/{shortUuid})

        The panel matches incoming subscription requests against rules that
        look at HTTP headers (User-Agent etc.). To replay that decision the
        endpoint takes a body of ``request_headers`` alongside the
        ``short_uuid``.

        :param short_uuid: short uuid of the user
        :param request_headers: header name → value mapping that mimics the
            VPN client's HTTP request
        :return: :class:`~remnacrow.models.SubpageConfig` with the resolved
            ``subpage_config_uuid`` (or ``None``) and ``webpage_allowed``
        """
        envelope: Envelope[SubpageConfig] = await self._client.request(
            "GET", f"/api/subscriptions/subpage-config/{short_uuid}",
            body={"requestHeaders": request_headers},
            response_type=Envelope[SubpageConfig],
        )
        return envelope.response

    async def get_request_history(
        self, *, size: int = 25, start: int = 0
    ) -> SubscriptionRequestHistory:
        """
        Paginated global subscription-request history across all users
        (GET /api/subscription-request-history)

        :param size: page size; defaults to 25 to match the panel default
        :param start: offset from the start of the history
        :return: :class:`~remnacrow.models.SubscriptionRequestHistory` with
            ``total`` and ``records``
        """
        params: dict[str, Any] = {"size": size, "start": start}
        envelope: Envelope[SubscriptionRequestHistory] = await self._client.request(
            "GET", "/api/subscription-request-history",
            params=params, response_type=Envelope[SubscriptionRequestHistory],
        )
        return envelope.response

    async def get_request_history_stats(self) -> SubscriptionRequestHistoryStats:
        """
        Aggregate stats over subscription-request history
        (GET /api/subscription-request-history/stats)

        :return: :class:`~remnacrow.models.SubscriptionRequestHistoryStats`
            with ``by_parsed_app`` (counts per detected client app) and
            ``hourly_request_stats`` (timeseries bucketed by hour)
        """
        envelope: Envelope[SubscriptionRequestHistoryStats] = await self._client.request(
            "GET", "/api/subscription-request-history/stats",
            response_type=Envelope[SubscriptionRequestHistoryStats],
        )
        return envelope.response
