from typing import Any

from ..models.common import DeletedResult, EventSentResult
from ..models.envelope import Envelope
from ..models.node_plugins import NodePlugin, NodePluginsPage, TorrentBlockerReportsPage
from .base import BaseRoute, pack


class NodePluginsRoute(BaseRoute):
    """``/api/node-plugins`` endpoints."""

    async def get_torrent_blocker_reports(
        self,
        *,
        size: int = 25,
        start: int = 0,
    ) -> TorrentBlockerReportsPage:
        envelope: Envelope[TorrentBlockerReportsPage] = await self._client.request(
            "GET",
            "/api/node-plugins/torrent-blocker",
            params={"size": size, "start": start},
            response_type=Envelope[TorrentBlockerReportsPage],
        )
        return envelope.response

    async def truncate_torrent_blocker_reports(self) -> TorrentBlockerReportsPage:
        envelope: Envelope[TorrentBlockerReportsPage] = await self._client.request(
            "DELETE",
            "/api/node-plugins/torrent-blocker/truncate",
            response_type=Envelope[TorrentBlockerReportsPage],
        )
        return envelope.response

    async def get_plugins(self) -> NodePluginsPage:
        envelope: Envelope[NodePluginsPage] = await self._client.request(
            "GET",
            "/api/node-plugins",
            response_type=Envelope[NodePluginsPage],
        )
        return envelope.response

    async def create_plugin(self, name: str) -> NodePlugin:
        envelope: Envelope[NodePlugin] = await self._client.request(
            "POST",
            "/api/node-plugins",
            body={"name": name},
            response_type=Envelope[NodePlugin],
        )
        return envelope.response

    async def update_plugin(
        self,
        uuid: str,
        *,
        name: str | None = None,
        plugin_config: dict[str, Any] | None = None,
    ) -> NodePlugin:
        body = pack(uuid=uuid, name=name, plugin_config=plugin_config)
        envelope: Envelope[NodePlugin] = await self._client.request(
            "PATCH",
            "/api/node-plugins",
            body=body,
            response_type=Envelope[NodePlugin],
        )
        return envelope.response

    async def get_plugin_by_uuid(self, uuid: str) -> NodePlugin:
        envelope: Envelope[NodePlugin] = await self._client.request(
            "GET",
            f"/api/node-plugins/{uuid}",
            response_type=Envelope[NodePlugin],
        )
        return envelope.response

    async def delete_plugin(self, uuid: str) -> bool:
        envelope: Envelope[DeletedResult] = await self._client.request(
            "DELETE",
            f"/api/node-plugins/{uuid}",
            response_type=Envelope[DeletedResult],
        )
        return envelope.response.is_deleted

    async def reorder_plugins(self, order: dict[str, int]) -> NodePluginsPage:
        body = {
            "items": [
                {"uuid": plugin_uuid, "viewPosition": position}
                for plugin_uuid, position in order.items()
            ]
        }
        envelope: Envelope[NodePluginsPage] = await self._client.request(
            "POST",
            "/api/node-plugins/actions/reorder",
            body=body,
            response_type=Envelope[NodePluginsPage],
        )
        return envelope.response

    async def clone_plugin(self, clone_from_uuid: str) -> NodePlugin:
        envelope: Envelope[NodePlugin] = await self._client.request(
            "POST",
            "/api/node-plugins/actions/clone",
            body={"cloneFromUuid": clone_from_uuid},
            response_type=Envelope[NodePlugin],
        )
        return envelope.response

    async def execute_command(
        self,
        command: dict[str, Any],
        *,
        node_uuids: list[str] | None = None,
    ) -> bool:
        if node_uuids is None:
            target_nodes = {"target": "allNodes"}
        else:
            target_nodes = {"target": "specificNodes", "nodeUuids": node_uuids}

        envelope: Envelope[EventSentResult] = await self._client.request(
            "POST",
            "/api/node-plugins/executor",
            body={"command": command, "targetNodes": target_nodes},
            response_type=Envelope[EventSentResult],
        )
        return envelope.response.event_sent
