from ..models.common import DeletedResult, EventSentResult
from ..models.envelope import Envelope
from ..models.squads import (
    InternalSquad,
    InternalSquadsPage,
    SquadAccessibleNodesResult,
)
from .base import BaseRoute, pack


class InternalSquadsRoute(BaseRoute):
    """``/api/internal-squads`` endpoints, mounted at ``RemnawaveClient.internal_squads``"""

    async def create(self, name: str, inbounds: list[str]) -> InternalSquad:
        """
        Create a new internal squad (POST /api/internal-squads)

        :param name: squad name (2-30 chars, matches ``^[A-Za-z0-9_\\s-]+$``)
        :param inbounds: list of inbound uuids the squad serves
        :return: the freshly created :class:`~remnacrow.models.InternalSquad`
        """
        envelope: Envelope[InternalSquad] = await self._client.request(
            "POST", "/api/internal-squads",
            body={"name": name, "inbounds": inbounds},
            response_type=Envelope[InternalSquad],
        )
        return envelope.response

    async def get_squads(self) -> InternalSquadsPage:
        """
        List every internal squad (GET /api/internal-squads)

        :return: :class:`~remnacrow.models.InternalSquadsPage` with ``total``
            and ``internal_squads`` ordered by view position
        """
        envelope: Envelope[InternalSquadsPage] = await self._client.request(
            "GET", "/api/internal-squads",
            response_type=Envelope[InternalSquadsPage],
        )
        return envelope.response

    async def update(
        self,
        uuid: str,
        *,
        name: str | None = None,
        inbounds: list[str] | None = None,
    ) -> InternalSquad:
        """
        Patch an existing internal squad (PATCH /api/internal-squads)

        Only the kwargs you pass are forwarded; ``None`` values are stripped.

        :param uuid: uuid of the squad to update
        :param name: new squad name
        :param inbounds: replacement list of inbound uuids
        :return: the updated :class:`~remnacrow.models.InternalSquad`
        """
        body = pack(uuid=uuid, name=name, inbounds=inbounds)
        envelope: Envelope[InternalSquad] = await self._client.request(
            "PATCH", "/api/internal-squads",
            body=body, response_type=Envelope[InternalSquad],
        )
        return envelope.response

    async def get_squad_by_uuid(self, uuid: str) -> InternalSquad:
        """
        Fetch a single internal squad (GET /api/internal-squads/{uuid})

        :param uuid: uuid of the squad
        :return: matching :class:`~remnacrow.models.InternalSquad`
        """
        envelope: Envelope[InternalSquad] = await self._client.request(
            "GET", f"/api/internal-squads/{uuid}",
            response_type=Envelope[InternalSquad],
        )
        return envelope.response

    async def delete(self, uuid: str) -> bool:
        """
        Remove an internal squad (DELETE /api/internal-squads/{uuid})

        :param uuid: uuid of the squad to delete
        :return: ``True`` if the panel removed the row (``isDeleted`` flag)
        """
        envelope: Envelope[DeletedResult] = await self._client.request(
            "DELETE", f"/api/internal-squads/{uuid}", response_type=Envelope[DeletedResult],
        )
        return envelope.response.is_deleted

    async def reorder(self, order: dict[str, int]) -> InternalSquadsPage:
        """
        Reorder internal squads in the panel
        (POST /api/internal-squads/actions/reorder)

        :param order: mapping of squad uuid → new ``view_position``
        :return: :class:`~remnacrow.models.InternalSquadsPage` reflecting the
            new positions
        """
        body = {
            "items": [
                {"uuid": squad_uuid, "viewPosition": position}
                for squad_uuid, position in order.items()
            ]
        }
        envelope: Envelope[InternalSquadsPage] = await self._client.request(
            "POST", "/api/internal-squads/actions/reorder",
            body=body, response_type=Envelope[InternalSquadsPage],
        )
        return envelope.response

    async def get_accessible_nodes(self, uuid: str) -> SquadAccessibleNodesResult:
        """
        List nodes this squad can reach
        (GET /api/internal-squads/{uuid}/accessible-nodes)

        :param uuid: uuid of the squad
        :return: :class:`~remnacrow.models.SquadAccessibleNodesResult` with
            ``squad_uuid`` and ``accessible_nodes``
        """
        envelope: Envelope[SquadAccessibleNodesResult] = await self._client.request(
            "GET", f"/api/internal-squads/{uuid}/accessible-nodes",
            response_type=Envelope[SquadAccessibleNodesResult],
        )
        return envelope.response

    async def add_all_users(self, uuid: str) -> bool:
        """
        Add every existing user to this internal squad
        (POST /api/internal-squads/{uuid}/bulk-actions/add-users)

        :param uuid: uuid of the squad
        :return: ``True`` if the bulk-add event was dispatched
            (``eventSent`` flag)
        """
        envelope: Envelope[EventSentResult] = await self._client.request(
            "POST", f"/api/internal-squads/{uuid}/bulk-actions/add-users",
            response_type=Envelope[EventSentResult],
        )
        return envelope.response.event_sent

    async def remove_all_users(self, uuid: str) -> bool:
        """
        Remove every user from this internal squad
        (DELETE /api/internal-squads/{uuid}/bulk-actions/remove-users)

        :param uuid: uuid of the squad
        :return: ``True`` if the bulk-remove event was dispatched
            (``eventSent`` flag)
        """
        envelope: Envelope[EventSentResult] = await self._client.request(
            "DELETE", f"/api/internal-squads/{uuid}/bulk-actions/remove-users",
            response_type=Envelope[EventSentResult],
        )
        return envelope.response.event_sent
