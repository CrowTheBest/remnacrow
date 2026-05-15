from typing import Any

from ..enums import NodeBulkAction
from ..models.envelope import Envelope
from ..models.nodes import Node
from .base import BaseRoute, pack


class NodesRoute(BaseRoute):
    """``/api/nodes`` endpoints, mounted at ``RemnawaveClient.nodes``"""

    async def create_node(
        self,
        name: str,
        address: str,
        config_profile_uuid: str,
        active_inbounds: list[str],
        *,
        port: int | None = None,
        is_traffic_tracking_active: bool | None = None,
        traffic_limit_bytes: int | None = None,
        notify_percent: int | None = None,
        traffic_reset_day: int | None = None,
        country_code: str | None = None,
        consumption_multiplier: float | None = None,
        provider_uuid: str | None = None,
        tags: list[str] | None = None,
        active_plugin_uuid: str | None = None,
    ) -> Node:
        """
        Create a new node (POST /api/nodes)

        :param name: display name shown in the panel (3-30 chars)
        :param address: hostname or IP the panel uses to reach the node
        :param config_profile_uuid: uuid of the config profile the node serves
        :param active_inbounds: list of inbound uuids enabled on this node
            (must reference inbounds inside ``config_profile_uuid``)
        :param port: node port (1-65535)
        :param is_traffic_tracking_active: enable per-node traffic accounting
        :param traffic_limit_bytes: total traffic cap in bytes (0 / None = unlimited)
        :param notify_percent: 0-100 — emit a webhook when cap usage hits this %
        :param traffic_reset_day: day of month (1-31) to auto-reset traffic
        :param country_code: ISO 3166-1 alpha-2 (2 chars); panel default is ``"XX"``
        :param consumption_multiplier: per-node multiplier applied to user traffic (0-100)
        :param provider_uuid: uuid of the linked infra provider, or ``None``
        :param tags: list of uppercase tags (regex ``^[A-Z0-9_:]+$``, max 10)
        :param active_plugin_uuid: uuid of an active plugin, or ``None``
        :return: the freshly created :class:`~remnacrow.models.Node`
        """
        body = pack(
            name=name, address=address, port=port,
            is_traffic_tracking_active=is_traffic_tracking_active,
            traffic_limit_bytes=traffic_limit_bytes, notify_percent=notify_percent,
            traffic_reset_day=traffic_reset_day, country_code=country_code,
            consumption_multiplier=consumption_multiplier, provider_uuid=provider_uuid,
            tags=tags, active_plugin_uuid=active_plugin_uuid,
        )
        body["configProfile"] = {
            "activeConfigProfileUuid": config_profile_uuid,
            "activeInbounds": active_inbounds,
        }
        envelope: Envelope[Node] = await self._client.request(
            "POST", "/api/nodes", body=body, response_type=Envelope[Node]
        )
        return envelope.response

    async def get_nodes(self) -> list[Node]:
        """
        List every node (GET /api/nodes)

        :return: list of :class:`~remnacrow.models.Node` ordered by view position
        """
        envelope: Envelope[list[Node]] = await self._client.request(
            "GET", "/api/nodes", response_type=Envelope[list[Node]]
        )
        return envelope.response

    async def update_node(
        self,
        uuid: str,
        *,
        name: str | None = None,
        address: str | None = None,
        port: int | None = None,
        is_traffic_tracking_active: bool | None = None,
        traffic_limit_bytes: int | None = None,
        notify_percent: int | None = None,
        traffic_reset_day: int | None = None,
        country_code: str | None = None,
        consumption_multiplier: float | None = None,
        config_profile_uuid: str | None = None,
        active_inbounds: list[str] | None = None,
        provider_uuid: str | None = None,
        tags: list[str] | None = None,
        active_plugin_uuid: str | None = None,
    ) -> Node:
        """
        Patch an existing node by uuid (PATCH /api/nodes)

        Only the fields explicitly passed are sent; ``None`` kwargs are
        stripped so existing panel values are preserved. To repoint the
        node's config profile, pass both ``config_profile_uuid`` and
        ``active_inbounds``.

        :param uuid: uuid of the node to update
        :param name: new display name
        :param address: new hostname or IP
        :param port: new port (1-65535)
        :param is_traffic_tracking_active: toggle per-node traffic tracking
        :param traffic_limit_bytes: new traffic cap in bytes
        :param notify_percent: new notify threshold (0-100)
        :param traffic_reset_day: new reset day of month (1-31)
        :param country_code: new ISO 3166-1 alpha-2 code
        :param consumption_multiplier: new per-node multiplier (0-100)
        :param config_profile_uuid: uuid of a new config profile to bind
        :param active_inbounds: replacement list of inbound uuids
        :param provider_uuid: new provider uuid (or ``None`` to detach)
        :param tags: replacement list of tags
        :param active_plugin_uuid: new active plugin uuid (or ``None``)
        :return: the updated :class:`~remnacrow.models.Node`
        """
        body = pack(
            uuid=uuid, name=name, address=address, port=port,
            is_traffic_tracking_active=is_traffic_tracking_active,
            traffic_limit_bytes=traffic_limit_bytes, notify_percent=notify_percent,
            traffic_reset_day=traffic_reset_day, country_code=country_code,
            consumption_multiplier=consumption_multiplier, provider_uuid=provider_uuid,
            tags=tags, active_plugin_uuid=active_plugin_uuid,
        )
        if config_profile_uuid is not None and active_inbounds is not None:
            body["configProfile"] = {
                "activeConfigProfileUuid": config_profile_uuid,
                "activeInbounds": active_inbounds,
            }

        envelope: Envelope[Node] = await self._client.request(
            "PATCH", "/api/nodes", body=body, response_type=Envelope[Node]
        )
        return envelope.response

    async def get_node_by_uuid(self, uuid: str) -> Node:
        """
        Fetch a single node (GET /api/nodes/{uuid})

        :param uuid: uuid of the node
        :return: matching :class:`~remnacrow.models.Node`
        """
        envelope: Envelope[Node] = await self._client.request(
            "GET", f"/api/nodes/{uuid}", response_type=Envelope[Node]
        )
        return envelope.response

    async def delete_node(self, uuid: str) -> bool:
        """
        Remove a node (DELETE /api/nodes/{uuid})

        :param uuid: uuid of the node to delete
        :return: ``True`` if the panel removed the row (``isDeleted`` flag)
        """
        data = await self._client.request(
            "DELETE", f"/api/nodes/{uuid}", response_type=dict
        )
        return bool(data["response"]["isDeleted"])

    async def reorder_nodes(self, order: dict[str, int]) -> list[Node]:
        """
        Reorder nodes in the panel (POST /api/nodes/actions/reorder)

        :param order: mapping of node uuid → new ``view_position``
        :return: full list of :class:`~remnacrow.models.Node` in the new order
        """
        body = {
            "nodes": [
                {"uuid": node_uuid, "viewPosition": position}
                for node_uuid, position in order.items()
            ]
        }
        envelope: Envelope[list[Node]] = await self._client.request(
            "POST", "/api/nodes/actions/reorder",
            body=body, response_type=Envelope[list[Node]],
        )
        return envelope.response

    async def restart_all_nodes(self, *, force_restart: bool | None = None) -> bool:
        """
        Trigger a restart on every node (POST /api/nodes/actions/restart-all)

        :param force_restart: if ``True``, restart even already-restarting nodes
        :return: ``True`` if the restart event was dispatched (``eventSent`` flag)
        """
        body = pack(force_restart=force_restart)
        data = await self._client.request(
            "POST", "/api/nodes/actions/restart-all",
            body=body, response_type=dict,
        )
        return bool(data["response"]["eventSent"])

    async def bulk_nodes_action(
        self, uuids: list[str], action: NodeBulkAction
    ) -> bool:
        """
        Run one :class:`~remnacrow.models.NodeBulkAction` on many nodes
        (POST /api/nodes/bulk-actions)

        :param uuids: list of node uuids to act on
        :param action: which action to perform — ``ENABLE`` / ``DISABLE`` /
            ``RESTART`` / ``RESET_TRAFFIC``
        :return: ``True`` if the action event was dispatched (``eventSent`` flag)
        """
        body = {"uuids": uuids, "action": action}
        data = await self._client.request(
            "POST", "/api/nodes/bulk-actions",
            body=body, response_type=dict,
        )
        return bool(data["response"]["eventSent"])

    async def bulk_profile_modification(
        self,
        uuids: list[str],
        config_profile_uuid: str,
        active_inbounds: list[str],
    ) -> bool:
        """
        Repoint many nodes at a new config profile + inbound set
        (POST /api/nodes/bulk-actions/profile-modification)

        :param uuids: list of node uuids to retarget
        :param config_profile_uuid: uuid of the config profile to apply
        :param active_inbounds: list of inbound uuids (must belong to
            ``config_profile_uuid``)
        :return: ``True`` if the modification event was dispatched
            (``eventSent`` flag)
        """
        body = {
            "uuids": uuids,
            "configProfile": {
                "activeConfigProfileUuid": config_profile_uuid,
                "activeInbounds": active_inbounds,
            },
        }
        data = await self._client.request(
            "POST", "/api/nodes/bulk-actions/profile-modification",
            body=body, response_type=dict,
        )
        return bool(data["response"]["eventSent"])

    async def bulk_update_nodes(
        self,
        uuids: list[str],
        *,
        country_code: str | None = None,
        consumption_multiplier: float | None = None,
        provider_uuid: str | None = None,
        tags: list[str] | None = None,
        active_plugin_uuid: str | None = None,
    ) -> bool:
        """Patch the same fields on many nodes (POST /api/nodes/bulk-actions/update)

        Only the kwargs you pass are forwarded to the panel; ``None`` values
        are stripped. At least one field must be provided.

        :param uuids: list of node uuids to update
        :param country_code: new ISO 3166-1 alpha-2 code
        :param consumption_multiplier: new per-node multiplier (0-100)
        :param provider_uuid: new provider uuid (or ``None`` to detach)
        :param tags: replacement list of tags
        :param active_plugin_uuid: new active plugin uuid (or ``None``)
        :return: ``True`` if the update event was dispatched (``eventSent`` flag)
        """
        fields = pack(
            country_code=country_code,
            consumption_multiplier=consumption_multiplier,
            provider_uuid=provider_uuid,
            tags=tags,
            active_plugin_uuid=active_plugin_uuid,
        )
        body: dict[str, Any] = {"uuids": uuids, "fields": fields}
        data = await self._client.request(
            "POST", "/api/nodes/bulk-actions/update",
            body=body, response_type=dict,
        )
        return bool(data["response"]["eventSent"])

    async def get_all_tags(self) -> list[str]:
        """
        List every tag in use across all nodes (GET /api/nodes/tags)

        :return: list of unique tag strings, ordering not guaranteed
        """
        data = await self._client.request(
            "GET", "/api/nodes/tags", response_type=dict
        )
        return list(data["response"]["tags"])

    async def disable_node(self, uuid: str) -> Node:
        """
        Disable a node (POST /api/nodes/{uuid}/actions/disable)

        Disabled nodes stay registered but stop accepting traffic.

        :param uuid: uuid of the node to disable
        :return: the updated :class:`~remnacrow.models.Node` with
            ``is_disabled=True``
        """
        envelope: Envelope[Node] = await self._client.request(
            "POST", f"/api/nodes/{uuid}/actions/disable",
            response_type=Envelope[Node],
        )
        return envelope.response

    async def enable_node(self, uuid: str) -> Node:
        """
        Enable a previously disabled node
        (POST /api/nodes/{uuid}/actions/enable)

        :param uuid: uuid of the node to enable
        :return: the updated :class:`~remnacrow.models.Node` with
            ``is_disabled=False``
        """
        envelope: Envelope[Node] = await self._client.request(
            "POST", f"/api/nodes/{uuid}/actions/enable",
            response_type=Envelope[Node],
        )
        return envelope.response

    async def reset_node_traffic(self, uuid: str) -> bool:
        """
        Zero out the node's accumulated traffic counter
        (POST /api/nodes/{uuid}/actions/reset-traffic)

        :param uuid: uuid of the node whose traffic to reset
        :return: ``True`` if the reset event was dispatched (``eventSent`` flag)
        """
        data = await self._client.request(
            "POST", f"/api/nodes/{uuid}/actions/reset-traffic",
            response_type=dict,
        )
        return bool(data["response"]["eventSent"])

    async def restart_node(self, uuid: str) -> bool:
        """
        Restart a single node (POST /api/nodes/{uuid}/actions/restart)

        :param uuid: uuid of the node to restart
        :return: ``True`` if the restart event was dispatched (``eventSent`` flag)
        """
        data = await self._client.request(
            "POST", f"/api/nodes/{uuid}/actions/restart",
            response_type=dict,
        )
        return bool(data["response"]["eventSent"])
