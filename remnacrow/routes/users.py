from datetime import datetime
from typing import Any

from ..enums import TrafficLimitStrategy, UserStatus
from ..models.common import AffectedRowsResult, DeletedResult, EventSentResult, TagsResult
from ..models.envelope import Envelope
from ..models.filters import Filter, Sort
from ..models.users import (
    AccessibleNodesResult,
    ResolvedUser,
    SubscriptionRequestHistory,
    User,
    UsersPage,
)
from .base import BaseRoute, build_list_params, pack


class UsersRoute(BaseRoute):
    """``/api/users`` endpoints, mounted at ``RemnawaveClient.users``"""

    async def create_user(
        self,
        username: str,
        *,
        expire_at: datetime,
        status: UserStatus | None = None,
        short_uuid: str | None = None,
        uuid: str | None = None,
        trojan_password: str | None = None,
        vless_uuid: str | None = None,
        ss_password: str | None = None,
        traffic_limit_bytes: int | None = None,
        traffic_limit_strategy: TrafficLimitStrategy | None = None,
        created_at: datetime | None = None,
        last_traffic_reset_at: datetime | None = None,
        description: str | None = None,
        tag: str | None = None,
        telegram_id: int | None = None,
        email: str | None = None,
        hwid_device_limit: int | None = None,
        active_internal_squads: list[str] | None = None,
        external_squad_uuid: str | None = None,
    ) -> User:
        """Create a new user (POST /api/users)

        Only ``username`` and ``expire_at`` are required. Pre-seeded
        identifiers and credentials (uuid, short_uuid, trojan_password,
        vless_uuid, ss_password) are intended for migrations; if omitted,
        the panel generates them.

        :param username: unique username for the new user
        :param expire_at: subscription expiration timestamp (UTC)
        :param status: initial :class:`~remnacrow.models.UserStatus`; defaults to ACTIVE panel-side
        :param short_uuid: pre-seeded short uuid (the token in the sub URL)
        :param uuid: pre-seeded primary uuid
        :param trojan_password: pre-seeded trojan password
        :param vless_uuid: pre-seeded vless uuid
        :param ss_password: pre-seeded shadowsocks password
        :param traffic_limit_bytes: total traffic cap in bytes (0 = unlimited)
        :param traffic_limit_strategy: cap reset :class:`~remnacrow.models.TrafficLimitStrategy` (NO_RESET / DAY / WEEK / MONTH / MONTH_ROLLING)
        :param created_at: override creation timestamp (migration use)
        :param last_traffic_reset_at: override last-reset timestamp
        :param description: free-form admin note
        :param tag: arbitrary tag for filtering and bulk ops
        :param telegram_id: linked Telegram id
        :param email: contact email
        :param hwid_device_limit: max concurrent devices (None = unlimited)
        :param active_internal_squads: list of internal squad uuids the user belongs to
        :param external_squad_uuid: uuid of an external squad the user belongs to
        :return: the freshly created :class:`~remnacrow.models.User`
        """
        body = pack(username=username, expire_at=expire_at, status=status, short_uuid=short_uuid, uuid=uuid,
                    trojan_password=trojan_password, vless_uuid=vless_uuid, ss_password=ss_password,
                    traffic_limit_bytes=traffic_limit_bytes, traffic_limit_strategy=traffic_limit_strategy,
                    created_at=created_at, last_traffic_reset_at=last_traffic_reset_at, description=description,
                    tag=tag, telegram_id=telegram_id, email=email, hwid_device_limit=hwid_device_limit,
                    active_internal_squads=active_internal_squads, external_squad_uuid=external_squad_uuid)
        envelope: Envelope[User] = await self._client.request(
            "POST", "/api/users", body=body, response_type=Envelope[User]
        )
        return envelope.response

    async def update_user(
        self,
        uuid: str,
        *,
        username: str | None = None,
        status: UserStatus | None = None,
        traffic_limit_bytes: int | None = None,
        traffic_limit_strategy: TrafficLimitStrategy | None = None,
        expire_at: datetime | None = None,
        description: str | None = None,
        tag: str | None = None,
        telegram_id: int | None = None,
        email: str | None = None,
        hwid_device_limit: int | None = None,
        active_internal_squads: list[str] | None = None,
        external_squad_uuid: str | None = None,
    ) -> User:
        """Patch an existing user by uuid (PATCH /api/users)

        Only the fields explicitly passed are sent; ``None`` kwargs are
        stripped so existing panel values are preserved.

        :param uuid: uuid of the user to update
        :param username: new username
        :param status: new :class:`~remnacrow.models.UserStatus` (ACTIVE / DISABLED)
        :param traffic_limit_bytes: new traffic cap in bytes (0 = unlimited)
        :param traffic_limit_strategy: new cap reset :class:`~remnacrow.models.TrafficLimitStrategy`
        :param expire_at: new expiration timestamp (UTC)
        :param description: new admin note
        :param tag: new tag
        :param telegram_id: new linked Telegram id
        :param email: new contact email
        :param hwid_device_limit: new device limit (None = unlimited)
        :param active_internal_squads: replacement list of internal squad uuids
        :param external_squad_uuid: new external squad uuid
        :return: the updated :class:`~remnacrow.models.User`
        """
        body = pack(uuid=uuid, username=username, status=status, traffic_limit_bytes=traffic_limit_bytes,
                    traffic_limit_strategy=traffic_limit_strategy, expire_at=expire_at, description=description,
                    tag=tag, telegram_id=telegram_id, email=email, hwid_device_limit=hwid_device_limit,
                    active_internal_squads=active_internal_squads, external_squad_uuid=external_squad_uuid)
        envelope: Envelope[User] = await self._client.request(
            "PATCH", "/api/users", body=body, response_type=Envelope[User]
        )
        return envelope.response

    async def get_users(
        self,
        *,
        size: int = 25,
        start: int = 0,
        filters: list[Filter] | None = None,
        sort: list[Sort] | None = None,
    ) -> UsersPage:
        """List users with pagination, optional filters and sorting (GET /api/users)

        Filter/sort params are not in the OpenAPI spec but are accepted by
        the panel — they mirror what the admin UI sends. Each value is
        JSON-encoded and sent as a query string.

        Supported filter modes (see :class:`~remnacrow.models.FilterMode`):
        ``contains``, ``startsWith``, ``endsWith``, ``equals``. If a
        :class:`~remnacrow.models.Filter` leaves ``mode=None``, the panel
        falls back to its server-side default for that column.

        Field hints (filter values):

        * ``status`` — any :class:`~remnacrow.models.UserStatus` value
        * ``tag`` — single tag string OR list for multi-select
          (typically paired with ``mode=FilterMode.EQUALS``)
        * ``nodeName`` — actually a node uuid (last-connected node),
          despite the field name
        * ``activeInternalSquads`` — squad uuid
        * use :class:`~remnacrow.models.UserField` for autocomplete on
          column names, including dotted paths like ``userTraffic.onlineAt``

        :param size: page size; defaults to 25 to match the panel default
        :param start: offset from the start of the user list
        :param filters: list of :class:`~remnacrow.models.Filter` constraints
            (each bundles field, value and optional mode together)
        :param sort: ordered list of :class:`~remnacrow.models.Sort` keys.
            Example: ``[Sort(UserField.USED_TRAFFIC_BYTES, desc=True)]`` for
            "biggest leechers first"
        :return: :class:`~remnacrow.models.UsersPage` with ``users`` (current page) and ``total`` —
            the count of users matching the query, **not** how many were
            returned in this request (use ``len(.users)`` for that)
        """
        envelope: Envelope[UsersPage] = await self._client.request(
            "GET",
            "/api/users",
            params=build_list_params(size, start, filters, sort),
            response_type=Envelope[UsersPage],
        )
        return envelope.response

    async def get_user_by_uuid(self, uuid: str) -> User:
        """Fetch a user by uuid (GET /api/users/{uuid})

        :param uuid: primary uuid of the user
        :return: the matching :class:`~remnacrow.models.User`
        """
        envelope: Envelope[User] = await self._client.request(
            "GET", f"/api/users/{uuid}", response_type=Envelope[User]
        )
        return envelope.response

    async def delete_user(self, uuid: str) -> bool:
        """Delete a user (DELETE /api/users/{uuid})

        :param uuid: uuid of the user to delete
        :return: True if the panel reports the user was deleted
        """
        envelope: Envelope[DeletedResult] = await self._client.request(
            "DELETE", f"/api/users/{uuid}", response_type=Envelope[DeletedResult]
        )
        return envelope.response.is_deleted

    async def get_all_tags(self) -> list[str]:
        """List every distinct tag currently assigned to any user (GET /api/users/tags)

        :return: list of tag strings
        """
        envelope: Envelope[TagsResult] = await self._client.request(
            "GET", "/api/users/tags", response_type=Envelope[TagsResult]
        )
        return envelope.response.tags

    async def get_user_accessible_nodes(self, uuid: str) -> AccessibleNodesResult:
        """List nodes the user can connect to via their active internal squads
        (GET /api/users/{uuid}/accessible-nodes)

        :param uuid: uuid of the user
        :return: :class:`~remnacrow.models.AccessibleNodesResult` with user_uuid and the list of nodes
        """
        envelope: Envelope[AccessibleNodesResult] = await self._client.request(
            "GET",
            f"/api/users/{uuid}/accessible-nodes",
            response_type=Envelope[AccessibleNodesResult],
        )
        return envelope.response

    async def get_user_subscription_request_history(
        self, uuid: str
    ) -> SubscriptionRequestHistory:
        """Audit log of subscription-URL fetches recorded for this user
        (GET /api/users/{uuid}/subscription-request-history)

        :param uuid: uuid of the user
        :return: :class:`~remnacrow.models.SubscriptionRequestHistory` with total count and records
        """
        envelope: Envelope[SubscriptionRequestHistory] = await self._client.request(
            "GET",
            f"/api/users/{uuid}/subscription-request-history",
            response_type=Envelope[SubscriptionRequestHistory],
        )
        return envelope.response

    async def get_user_by_short_uuid(self, short_uuid: str) -> User:
        """Fetch a user by short uuid (GET /api/users/by-short-uuid/{shortUuid})

        The short uuid is the token embedded in the user's subscription URL.

        :param short_uuid: short uuid of the user
        :return: the matching :class:`~remnacrow.models.User`
        """
        envelope: Envelope[User] = await self._client.request(
            "GET",
            f"/api/users/by-short-uuid/{short_uuid}",
            response_type=Envelope[User],
        )
        return envelope.response

    async def get_user_by_username(self, username: str) -> User:
        """Fetch a user by username (GET /api/users/by-username/{username})

        Username is unique panel-side, so at most one match.

        :param username: username of the user
        :return: the matching :class:`~remnacrow.models.User`
        """
        envelope: Envelope[User] = await self._client.request(
            "GET",
            f"/api/users/by-username/{username}",
            response_type=Envelope[User],
        )
        return envelope.response

    async def get_user_by_id(self, id: int) -> User:
        """Fetch a user by panel-internal numeric id (GET /api/users/by-id/{id})

        :param id: numeric panel-internal id
        :return: the matching :class:`~remnacrow.models.User`
        """
        envelope: Envelope[User] = await self._client.request(
            "GET", f"/api/users/by-id/{id}", response_type=Envelope[User]
        )
        return envelope.response

    async def get_users_by_telegram_id(self, telegram_id: int) -> list[User]:
        """Fetch all users linked to a Telegram id
        (GET /api/users/by-telegram-id/{telegramId})

        Telegram id is not unique panel-side — multiple users may share one.

        :param telegram_id: Telegram id
        :return: list of :class:`~remnacrow.models.User` linked to that Telegram id (possibly empty)
        """
        envelope: Envelope[list[User]] = await self._client.request(
            "GET",
            f"/api/users/by-telegram-id/{telegram_id}",
            response_type=Envelope[list[User]],
        )
        return envelope.response

    async def get_users_by_email(self, email: str) -> list[User]:
        """Fetch all users sharing an email address (GET /api/users/by-email/{email})

        :param email: email address
        :return: list of :class:`~remnacrow.models.User` with that email (possibly empty)
        """
        envelope: Envelope[list[User]] = await self._client.request(
            "GET",
            f"/api/users/by-email/{email}",
            response_type=Envelope[list[User]],
        )
        return envelope.response

    async def get_users_by_tag(self, tag: str) -> list[User]:
        """Fetch all users that carry the given tag (GET /api/users/by-tag/{tag})

        :param tag: tag string
        :return: list of :class:`~remnacrow.models.User` with that tag (possibly empty)
        """
        envelope: Envelope[list[User]] = await self._client.request(
            "GET",
            f"/api/users/by-tag/{tag}",
            response_type=Envelope[list[User]],
        )
        return envelope.response

    async def revoke_user_subscription(
        self,
        uuid: str,
        *,
        revoke_only_passwords: bool | None = None,
        short_uuid: str | None = None,
    ) -> User:
        """Rotate the user's subscription URL and inbound credentials
        (POST /api/users/{uuid}/actions/revoke)

        :param uuid: uuid of the user
        :param revoke_only_passwords: if True, rotate only protocol passwords/UUIDs
            and keep the subscription URL the same
        :param short_uuid: force a specific new short uuid instead of letting the panel generate one
        :return: the updated :class:`~remnacrow.models.User` with new credentials
        """
        body = pack(revoke_only_passwords=revoke_only_passwords, short_uuid=short_uuid)
        envelope: Envelope[User] = await self._client.request(
            "POST",
            f"/api/users/{uuid}/actions/revoke",
            body=body or None,
            response_type=Envelope[User],
        )
        return envelope.response

    async def disable_user(self, uuid: str) -> User:
        """Disable a user, cutting off panel access
        (POST /api/users/{uuid}/actions/disable)

        :param uuid: uuid of the user
        :return: the updated :class:`~remnacrow.models.User` (status=DISABLED)
        """
        envelope: Envelope[User] = await self._client.request(
            "POST",
            f"/api/users/{uuid}/actions/disable",
            response_type=Envelope[User],
        )
        return envelope.response

    async def enable_user(self, uuid: str) -> User:
        """Re-enable a previously disabled user
        (POST /api/users/{uuid}/actions/enable)

        :param uuid: uuid of the user
        :return: the updated :class:`~remnacrow.models.User` (status=ACTIVE)
        """
        envelope: Envelope[User] = await self._client.request(
            "POST",
            f"/api/users/{uuid}/actions/enable",
            response_type=Envelope[User],
        )
        return envelope.response

    async def reset_user_traffic(self, uuid: str) -> User:
        """Zero the user's current-period traffic counter
        (POST /api/users/{uuid}/actions/reset-traffic)

        :param uuid: uuid of the user
        :return: the updated :class:`~remnacrow.models.User`
        """
        envelope: Envelope[User] = await self._client.request(
            "POST",
            f"/api/users/{uuid}/actions/reset-traffic",
            response_type=Envelope[User],
        )
        return envelope.response

    async def resolve_user(
        self,
        *,
        uuid: str | None = None,
        id: int | None = None,
        short_uuid: str | None = None,
        username: str | None = None,
    ) -> ResolvedUser:
        """Look up a user by any one of several identifiers (POST /api/users/resolve)

        Useful when you have one identifier and need to canonicalize to uuid
        without fetching the full User payload.

        :param uuid: primary uuid
        :param id: panel-internal numeric id
        :param short_uuid: short uuid
        :param username: username
        :return: :class:`~remnacrow.models.ResolvedUser` with uuid, username, id, short_uuid
        """
        body = pack(uuid=uuid, id=id, short_uuid=short_uuid, username=username)
        envelope: Envelope[ResolvedUser] = await self._client.request(
            "POST",
            "/api/users/resolve",
            body=body,
            response_type=Envelope[ResolvedUser],
        )
        return envelope.response

    async def bulk_delete_users_by_status(self, status: UserStatus) -> int:
        """Delete every user with the given status
        (POST /api/users/bulk/delete-by-status)

        :param status: :class:`~remnacrow.models.UserStatus` of users to delete
        :return: number of users actually deleted
        """
        envelope: Envelope[AffectedRowsResult] = await self._client.request(
            "POST",
            "/api/users/bulk/delete-by-status",
            body=pack(status=status),
            response_type=Envelope[AffectedRowsResult],
        )
        return envelope.response.affected_rows

    async def bulk_delete_users(self, uuids: list[str]) -> int:
        """Delete the listed users (POST /api/users/bulk/delete)

        :param uuids: list of user uuids to delete
        :return: number of users actually deleted
        """
        envelope: Envelope[AffectedRowsResult] = await self._client.request(
            "POST",
            "/api/users/bulk/delete",
            body=pack(uuids=uuids),
            response_type=Envelope[AffectedRowsResult],
        )
        return envelope.response.affected_rows

    async def bulk_revoke_users_subscription(self, uuids: list[str]) -> int:
        """Rotate subscription URLs and credentials for the listed users
        (POST /api/users/bulk/revoke-subscription)

        :param uuids: list of user uuids
        :return: number of users whose subscriptions were rotated
        """
        envelope: Envelope[AffectedRowsResult] = await self._client.request(
            "POST",
            "/api/users/bulk/revoke-subscription",
            body=pack(uuids=uuids),
            response_type=Envelope[AffectedRowsResult],
        )
        return envelope.response.affected_rows

    async def bulk_reset_user_traffic(self, uuids: list[str]) -> int:
        """Zero the current-period traffic counter for the listed users
        (POST /api/users/bulk/reset-traffic)

        :param uuids: list of user uuids
        :return: number of users whose traffic was reset
        """
        envelope: Envelope[AffectedRowsResult] = await self._client.request(
            "POST",
            "/api/users/bulk/reset-traffic",
            body=pack(uuids=uuids),
            response_type=Envelope[AffectedRowsResult],
        )
        return envelope.response.affected_rows

    async def bulk_update_users(self, uuids: list[str], fields: dict[str, Any]) -> int:
        """Apply the same field updates to a list of users
        (POST /api/users/bulk/update)

        :param uuids: list of user uuids to update
        :param fields: raw update payload with camelCase keys
            (same shape ``update_user`` would build internally), used as-is
        :return: number of users updated
        """
        envelope: Envelope[AffectedRowsResult] = await self._client.request(
            "POST",
            "/api/users/bulk/update",
            body=pack(uuids=uuids, fields=fields),
            response_type=Envelope[AffectedRowsResult],
        )
        return envelope.response.affected_rows

    async def bulk_update_users_internal_squads(
        self, uuids: list[str], active_internal_squads: list[str]
    ) -> int:
        """Replace active internal squads for the listed users
        (POST /api/users/bulk/update-squads)

        :param uuids: list of user uuids
        :param active_internal_squads: replacement list of internal squad uuids
        :return: number of users updated
        """
        envelope: Envelope[AffectedRowsResult] = await self._client.request(
            "POST",
            "/api/users/bulk/update-squads",
            body=pack(uuids=uuids, active_internal_squads=active_internal_squads),
            response_type=Envelope[AffectedRowsResult],
        )
        return envelope.response.affected_rows

    async def bulk_extend_expiration_date(
        self, uuids: list[str], extend_days: int
    ) -> int:
        """Push ``expireAt`` forward by ``extend_days`` for the listed users
        (POST /api/users/bulk/extend-expiration-date)

        :param uuids: list of user uuids
        :param extend_days: number of days to add to each user's expireAt
        :return: number of users whose expiration was extended
        """
        envelope: Envelope[AffectedRowsResult] = await self._client.request(
            "POST",
            "/api/users/bulk/extend-expiration-date",
            body=pack(uuids=uuids, extend_days=extend_days),
            response_type=Envelope[AffectedRowsResult],
        )
        return envelope.response.affected_rows

    async def bulk_all_update_users(
        self,
        *,
        status: UserStatus | None = None,
        traffic_limit_bytes: int | None = None,
        traffic_limit_strategy: TrafficLimitStrategy | None = None,
        expire_at: datetime | None = None,
        description: str | None = None,
        telegram_id: int | None = None,
        email: str | None = None,
        tag: str | None = None,
        hwid_device_limit: int | None = None,
    ) -> bool:
        """Apply the given changes to ALL users on the panel
        (POST /api/users/bulk/all/update)

        Runs as a background event on the panel side and returns immediately.
        The returned flag indicates whether the event was scheduled,
        **not** whether it has finished executing.

        :param status: new :class:`~remnacrow.models.UserStatus` for every user
        :param traffic_limit_bytes: new traffic cap for every user (bytes)
        :param traffic_limit_strategy: new cap reset :class:`~remnacrow.models.TrafficLimitStrategy` for every user
        :param expire_at: new expiration timestamp for every user (UTC)
        :param description: new admin note for every user
        :param telegram_id: new linked Telegram id for every user
        :param email: new contact email for every user
        :param tag: new tag for every user
        :param hwid_device_limit: new device limit for every user
        :return: True if the panel scheduled the update event
        """
        body = pack(status=status, traffic_limit_bytes=traffic_limit_bytes,
                    traffic_limit_strategy=traffic_limit_strategy, expire_at=expire_at, description=description,
                    telegram_id=telegram_id, email=email, tag=tag, hwid_device_limit=hwid_device_limit)
        envelope: Envelope[EventSentResult] = await self._client.request(
            "POST",
            "/api/users/bulk/all/update",
            body=body or None,
            response_type=Envelope[EventSentResult],
        )
        return envelope.response.event_sent

    async def bulk_all_reset_user_traffic(self) -> bool:
        """Zero the traffic counter for ALL users on the panel
        (POST /api/users/bulk/all/reset-traffic)

        Async event — returns once the panel has scheduled the work,
        not when it has completed.

        :return: True if the reset event was scheduled
        """
        envelope: Envelope[EventSentResult] = await self._client.request(
            "POST",
            "/api/users/bulk/all/reset-traffic",
            response_type=Envelope[EventSentResult],
        )
        return envelope.response.event_sent

    async def bulk_all_extend_expiration_date(self, extend_days: int) -> bool:
        """Push ``expireAt`` forward by ``extend_days`` for ALL users on the panel
        (POST /api/users/bulk/all/extend-expiration-date)

        Async event — returns once the panel has scheduled the work.

        :param extend_days: number of days to add to every user's expireAt
        :return: True if the extension event was scheduled
        """
        envelope: Envelope[EventSentResult] = await self._client.request(
            "POST",
            "/api/users/bulk/all/extend-expiration-date",
            body=pack(extend_days=extend_days),
            response_type=Envelope[EventSentResult],
        )
        return envelope.response.event_sent
