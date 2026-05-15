from datetime import datetime
from typing import Any

from ..models.envelope import Envelope
from ..models.stats import (
    BandwidthStats,
    BandwidthUsageChart,
    LegacyNodeUserUsage,
    LegacyUserNodeUsage,
    NodeUsersUsageChart,
    NodesWeeklyStats,
    Recap,
    SystemStats,
    TorrentBlockerStats,
)
from .base import BaseRoute


def _isoformat(value: datetime | str) -> str:
    """Normalize a start/end query param to an ISO string the panel accepts"""
    return value.isoformat() if isinstance(value, datetime) else value


class StatsRoute(BaseRoute):
    """``/api/system/stats``, ``/api/bandwidth-stats`` and ``/api/node-plugins/torrent-blocker/stats``,
    mounted at ``RemnawaveClient.stats``"""

    async def get_system_stats(self) -> SystemStats:
        """
        Live system snapshot — CPU/memory/uptime + user-state counters
        (GET /api/system/stats)

        :return: :class:`~remnacrow.models.SystemStats` with ``cpu``,
            ``memory``, ``uptime``, ``timestamp``, ``users``,
            ``online_stats``, ``nodes``
        """
        envelope: Envelope[SystemStats] = await self._client.request(
            "GET", "/api/system/stats",
            response_type=Envelope[SystemStats],
        )
        return envelope.response

    async def get_bandwidth_stats(self) -> BandwidthStats:
        """
        Calendar-bucketed bandwidth totals
        (GET /api/system/stats/bandwidth)

        Each bucket carries the current value, the previous comparable
        period, and the difference (formatted byte strings as the panel
        renders them).

        :return: :class:`~remnacrow.models.BandwidthStats` with five
            :class:`~remnacrow.models.BandwidthPeriod` buckets: 2-day,
            7-day, 30-day, calendar-month, and current-year
        """
        envelope: Envelope[BandwidthStats] = await self._client.request(
            "GET", "/api/system/stats/bandwidth",
            response_type=Envelope[BandwidthStats],
        )
        return envelope.response

    async def get_nodes_weekly_stats(self) -> NodesWeeklyStats:
        """
        Per-node daily totals for the trailing seven days
        (GET /api/system/stats/nodes)

        :return: :class:`~remnacrow.models.NodesWeeklyStats` with
            ``last_seven_days`` — flat list of (node_name, date, total_bytes)
        """
        envelope: Envelope[NodesWeeklyStats] = await self._client.request(
            "GET", "/api/system/stats/nodes",
            response_type=Envelope[NodesWeeklyStats],
        )
        return envelope.response

    async def get_recap(self) -> Recap:
        """
        Roll-up: month-to-date users + traffic, lifetime totals, panel
        version, init date (GET /api/system/stats/recap)

        :return: :class:`~remnacrow.models.Recap`
        """
        envelope: Envelope[Recap] = await self._client.request(
            "GET", "/api/system/stats/recap",
            response_type=Envelope[Recap],
        )
        return envelope.response

    async def get_nodes_usage(
        self,
        *,
        top_nodes_limit: int,
        start: datetime | str,
        end: datetime | str,
    ) -> BandwidthUsageChart:
        """
        Top-N node usage with sparkline + time series for a date range
        (GET /api/bandwidth-stats/nodes)

        :param top_nodes_limit: how many nodes to keep in ``top_nodes``
        :param start: range start — ``datetime`` (ISO-formatted) or raw string
        :param end: range end — ``datetime`` (ISO-formatted) or raw string
        :return: :class:`~remnacrow.models.BandwidthUsageChart` with
            ``categories``, ``sparkline_data``, ``top_nodes``, ``series``
        """
        params: dict[str, Any] = {
            "topNodesLimit": top_nodes_limit,
            "start": _isoformat(start),
            "end": _isoformat(end),
        }
        envelope: Envelope[BandwidthUsageChart] = await self._client.request(
            "GET", "/api/bandwidth-stats/nodes",
            params=params, response_type=Envelope[BandwidthUsageChart],
        )
        return envelope.response

    async def get_node_users_usage(
        self,
        node_uuid: str,
        *,
        top_users_limit: int,
        start: datetime | str,
        end: datetime | str,
    ) -> NodeUsersUsageChart:
        """
        Per-node top user usage for a date range
        (GET /api/bandwidth-stats/nodes/{uuid}/users)

        :param node_uuid: uuid of the node
        :param top_users_limit: how many users to keep in ``top_users``
        :param start: range start — ``datetime`` or raw string
        :param end: range end — ``datetime`` or raw string
        :return: :class:`~remnacrow.models.NodeUsersUsageChart` with
            ``categories``, ``sparkline_data``, ``top_users``
        """
        params: dict[str, Any] = {
            "topUsersLimit": top_users_limit,
            "start": _isoformat(start),
            "end": _isoformat(end),
        }
        envelope: Envelope[NodeUsersUsageChart] = await self._client.request(
            "GET", f"/api/bandwidth-stats/nodes/{node_uuid}/users",
            params=params, response_type=Envelope[NodeUsersUsageChart],
        )
        return envelope.response

    async def get_node_users_usage_legacy(
        self,
        node_uuid: str,
        *,
        start: datetime | str,
        end: datetime | str,
    ) -> list[LegacyNodeUserUsage]:
        """
        Flat per-user daily totals on a single node — pre-chart format
        (GET /api/bandwidth-stats/nodes/{uuid}/users/legacy)

        :param node_uuid: uuid of the node
        :param start: range start
        :param end: range end
        :return: list of :class:`~remnacrow.models.LegacyNodeUserUsage`
            entries (user_uuid, username, node_uuid, total, date)
        """
        params: dict[str, Any] = {
            "start": _isoformat(start),
            "end": _isoformat(end),
        }
        envelope: Envelope[list[LegacyNodeUserUsage]] = await self._client.request(
            "GET", f"/api/bandwidth-stats/nodes/{node_uuid}/users/legacy",
            params=params, response_type=Envelope[list[LegacyNodeUserUsage]],
        )
        return envelope.response

    async def get_user_usage(
        self,
        user_uuid: str,
        *,
        top_nodes_limit: int,
        start: datetime | str,
        end: datetime | str,
    ) -> BandwidthUsageChart:
        """
        Per-user usage across nodes with sparkline + time series
        (GET /api/bandwidth-stats/users/{uuid})

        :param user_uuid: uuid of the user
        :param top_nodes_limit: how many nodes to keep in ``top_nodes``
        :param start: range start
        :param end: range end
        :return: :class:`~remnacrow.models.BandwidthUsageChart` — same shape
            as :meth:`get_nodes_usage` but scoped to one user's traffic
        """
        params: dict[str, Any] = {
            "topNodesLimit": top_nodes_limit,
            "start": _isoformat(start),
            "end": _isoformat(end),
        }
        envelope: Envelope[BandwidthUsageChart] = await self._client.request(
            "GET", f"/api/bandwidth-stats/users/{user_uuid}",
            params=params, response_type=Envelope[BandwidthUsageChart],
        )
        return envelope.response

    async def get_user_usage_legacy(
        self,
        user_uuid: str,
        *,
        start: datetime | str,
        end: datetime | str,
    ) -> list[LegacyUserNodeUsage]:
        """
        Flat per-node daily totals for one user — pre-chart format
        (GET /api/bandwidth-stats/users/{uuid}/legacy)

        :param user_uuid: uuid of the user
        :param start: range start
        :param end: range end
        :return: list of :class:`~remnacrow.models.LegacyUserNodeUsage`
            entries (user_uuid, node_uuid, node_name, country_code, total, date)
        """
        params: dict[str, Any] = {
            "start": _isoformat(start),
            "end": _isoformat(end),
        }
        envelope: Envelope[list[LegacyUserNodeUsage]] = await self._client.request(
            "GET", f"/api/bandwidth-stats/users/{user_uuid}/legacy",
            params=params, response_type=Envelope[list[LegacyUserNodeUsage]],
        )
        return envelope.response

    async def get_torrent_blocker_stats(self) -> TorrentBlockerStats:
        """
        Aggregate torrent-blocker plugin stats — distinct counts +
        top users + top nodes
        (GET /api/node-plugins/torrent-blocker/stats)

        :return: :class:`~remnacrow.models.TorrentBlockerStats`
        """
        envelope: Envelope[TorrentBlockerStats] = await self._client.request(
            "GET", "/api/node-plugins/torrent-blocker/stats",
            response_type=Envelope[TorrentBlockerStats],
        )
        return envelope.response
