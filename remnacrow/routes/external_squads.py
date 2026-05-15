from typing import Any

from ..models.envelope import Envelope
from ..models.squads import ExternalSquad, ExternalSquadsPage
from .base import BaseRoute, pack


class ExternalSquadsRoute(BaseRoute):
    """``/api/external-squads`` endpoints, mounted at ``RemnawaveClient.external_squads``"""

    async def create(self, name: str) -> ExternalSquad:
        """
        Create a new external squad (POST /api/external-squads)

        Only ``name`` is required at creation time; the panel seeds defaults
        for templates / subscription settings / host overrides. Use
        :meth:`update` to fill those in.

        :param name: squad name (2-30 chars, matches ``^[A-Za-z0-9_\\s-]+$``)
        :return: the freshly created :class:`~remnacrow.models.ExternalSquad`
        """
        envelope: Envelope[ExternalSquad] = await self._client.request(
            "POST", "/api/external-squads",
            body={"name": name}, response_type=Envelope[ExternalSquad],
        )
        return envelope.response

    async def get_squads(self) -> ExternalSquadsPage:
        """
        List every external squad (GET /api/external-squads)

        :return: :class:`~remnacrow.models.ExternalSquadsPage` with ``total``
            and ``external_squads`` ordered by view position
        """
        envelope: Envelope[ExternalSquadsPage] = await self._client.request(
            "GET", "/api/external-squads",
            response_type=Envelope[ExternalSquadsPage],
        )
        return envelope.response

    async def update(
        self,
        uuid: str,
        *,
        name: str | None = None,
        templates: list[dict[str, Any]] | None = None,
        subscription_settings: dict[str, Any] | None = None,
        host_overrides: dict[str, Any] | None = None,
        response_headers: dict[str, str] | None = None,
        hwid_settings: dict[str, Any] | None = None,
        custom_remarks: dict[str, list[str]] | None = None,
        subpage_config_uuid: str | None = None,
    ) -> ExternalSquad:
        """
        Patch an existing external squad (PATCH /api/external-squads)

        Only the kwargs you pass are forwarded; ``None`` values are
        stripped. Sub-objects are accepted as raw dicts (already camelCase /
        PascalCase as the panel expects on the wire) to keep the API flat
        without forcing the caller through 20+ leaf kwargs.

        :param uuid: uuid of the squad to update
        :param name: new squad name
        :param templates: list of ``{"templateUuid": str, "templateType": str}``
            entries (template type ∈ :class:`~remnacrow.models.SubscriptionTemplateType`)
        :param subscription_settings: ``{profileTitle, supportLink,
            profileUpdateInterval, isProfileWebpageUrlEnabled,
            serveJsonAtBaseSubscription, isShowCustomRemarks, happAnnounce,
            happRouting, randomizeHosts}``
        :param host_overrides: ``{serverDescription, vlessRouteId}``
        :param response_headers: header name → value mapping appended to
            subscription HTTP responses
        :param hwid_settings: ``{enabled, fallbackDeviceLimit, maxDevicesAnnounce}``
        :param custom_remarks: per-user-state remark templates with keys
            ``expiredUsers``, ``limitedUsers``, ``disabledUsers``,
            ``emptyHosts``, ``HWIDMaxDevicesExceeded``, ``HWIDNotSupported``
            (note the PascalCase prefix on the two HWID keys)
        :param subpage_config_uuid: uuid of a subpage config to bind
        :return: the updated :class:`~remnacrow.models.ExternalSquad`
        """
        body = pack(
            uuid=uuid, name=name, templates=templates,
            subscription_settings=subscription_settings,
            host_overrides=host_overrides, response_headers=response_headers,
            hwid_settings=hwid_settings, subpage_config_uuid=subpage_config_uuid,
        )
        if custom_remarks is not None:
            body["customRemarks"] = custom_remarks

        envelope: Envelope[ExternalSquad] = await self._client.request(
            "PATCH", "/api/external-squads",
            body=body, response_type=Envelope[ExternalSquad],
        )
        return envelope.response

    async def get_squad_by_uuid(self, uuid: str) -> ExternalSquad:
        """
        Fetch a single external squad (GET /api/external-squads/{uuid})

        :param uuid: uuid of the squad
        :return: matching :class:`~remnacrow.models.ExternalSquad`
        """
        envelope: Envelope[ExternalSquad] = await self._client.request(
            "GET", f"/api/external-squads/{uuid}",
            response_type=Envelope[ExternalSquad],
        )
        return envelope.response

    async def delete(self, uuid: str) -> bool:
        """
        Remove an external squad (DELETE /api/external-squads/{uuid})

        :param uuid: uuid of the squad to delete
        :return: ``True`` if the panel removed the row (``isDeleted`` flag)
        """
        data = await self._client.request(
            "DELETE", f"/api/external-squads/{uuid}", response_type=dict,
        )
        return bool(data["response"]["isDeleted"])

    async def reorder(self, order: dict[str, int]) -> ExternalSquadsPage:
        """
        Reorder external squads in the panel
        (POST /api/external-squads/actions/reorder)

        :param order: mapping of squad uuid → new ``view_position``
        :return: :class:`~remnacrow.models.ExternalSquadsPage` reflecting
            the new positions
        """
        body = {
            "items": [
                {"uuid": squad_uuid, "viewPosition": position}
                for squad_uuid, position in order.items()
            ]
        }
        envelope: Envelope[ExternalSquadsPage] = await self._client.request(
            "POST", "/api/external-squads/actions/reorder",
            body=body, response_type=Envelope[ExternalSquadsPage],
        )
        return envelope.response

    async def add_all_users(self, uuid: str) -> bool:
        """
        Add every existing user to this external squad
        (POST /api/external-squads/{uuid}/bulk-actions/add-users)

        :param uuid: uuid of the squad
        :return: ``True`` if the bulk-add event was dispatched
            (``eventSent`` flag)
        """
        data = await self._client.request(
            "POST", f"/api/external-squads/{uuid}/bulk-actions/add-users",
            response_type=dict,
        )
        return bool(data["response"]["eventSent"])

    async def remove_all_users(self, uuid: str) -> bool:
        """
        Remove every user from this external squad
        (DELETE /api/external-squads/{uuid}/bulk-actions/remove-users)

        :param uuid: uuid of the squad
        :return: ``True`` if the bulk-remove event was dispatched
            (``eventSent`` flag)
        """
        data = await self._client.request(
            "DELETE", f"/api/external-squads/{uuid}/bulk-actions/remove-users",
            response_type=dict,
        )
        return bool(data["response"]["eventSent"])
