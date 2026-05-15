from datetime import datetime

from .base import Struct


# .response.cpu on /api/system/stats
class CpuStats(Struct):
    cores: float


# .response.memory on /api/system/stats
class MemoryStats(Struct):
    total: float
    free: float
    used: float


# .response.users on /api/system/stats
class UsersStats(Struct):
    status_counts: dict[str, float]
    total_users: float


# .response.onlineStats on /api/system/stats
class OnlineStats(Struct):
    last_day: float
    last_week: float
    never_online: float
    online_now: float


# .response.nodes on /api/system/stats — short summary, not per-node
class NodesSummaryStats(Struct):
    total_online: float
    total_bytes_lifetime: str


# .response on /api/system/stats
class SystemStats(Struct):
    cpu: CpuStats
    memory: MemoryStats
    uptime: float
    timestamp: float
    users: UsersStats
    online_stats: OnlineStats
    nodes: NodesSummaryStats


# .response.bandwidth* entries on /api/system/stats/bandwidth
class BandwidthPeriod(Struct):
    current: str
    previous: str
    difference: str


# .response on /api/system/stats/bandwidth
class BandwidthStats(Struct):
    bandwidth_last_two_days: BandwidthPeriod
    bandwidth_last_seven_days: BandwidthPeriod
    bandwidth_last_30_days: BandwidthPeriod
    bandwidth_calendar_month: BandwidthPeriod
    bandwidth_current_year: BandwidthPeriod


# item of .response.lastSevenDays[] on /api/system/stats/nodes
class NodeDailyStat(Struct):
    node_name: str
    date: str
    total_bytes: str


# .response on /api/system/stats/nodes
class NodesWeeklyStats(Struct):
    last_seven_days: list[NodeDailyStat]


# .response.thisMonth on /api/system/stats/recap
class RecapThisMonth(Struct):
    users: float
    traffic: str


# .response.total on /api/system/stats/recap
class RecapTotal(Struct):
    users: float
    nodes: float
    traffic: str
    nodes_ram: str
    nodes_cpu_cores: float
    distinct_countries: float


# .response on /api/system/stats/recap
class Recap(Struct):
    this_month: RecapThisMonth
    total: RecapTotal
    version: str
    init_date: datetime


# item of .topNodes[] on /api/bandwidth-stats/nodes
# and .topNodes[] on /api/bandwidth-stats/users/{uuid}
class UsageTopNode(Struct):
    uuid: str
    color: str
    name: str
    country_code: str
    total: float


# item of .series[] on /api/bandwidth-stats/{nodes,users/{uuid}}
class UsageSeries(Struct):
    uuid: str
    name: str
    color: str
    country_code: str
    total: float
    data: list[float]


# .response on /api/bandwidth-stats/nodes — same shape on
# /api/bandwidth-stats/users/{uuid} (different semantic axis)
class BandwidthUsageChart(Struct):
    categories: list[str]
    sparkline_data: list[float]
    top_nodes: list[UsageTopNode]
    series: list[UsageSeries]


# item of .topUsers[] on /api/bandwidth-stats/nodes/{uuid}/users
class UsageTopUser(Struct):
    color: str
    username: str
    total: float


# .response on /api/bandwidth-stats/nodes/{uuid}/users
class NodeUsersUsageChart(Struct):
    categories: list[str]
    sparkline_data: list[float]
    top_users: list[UsageTopUser]


# item of .response[] on /api/bandwidth-stats/nodes/{uuid}/users/legacy
class LegacyNodeUserUsage(Struct):
    user_uuid: str
    username: str
    node_uuid: str
    total: float
    date: str


# item of .response[] on /api/bandwidth-stats/users/{uuid}/legacy
class LegacyUserNodeUsage(Struct):
    user_uuid: str
    node_uuid: str
    node_name: str
    country_code: str
    total: float
    date: str


# .response.stats on /api/node-plugins/torrent-blocker/stats
class TorrentBlockerStatsSummary(Struct):
    distinct_nodes: float
    distinct_users: float
    total_reports: float
    reports_last_24_hours: float


# item of .response.topUsers[] on /api/node-plugins/torrent-blocker/stats
class TorrentBlockerTopUser(Struct):
    uuid: str
    color: str
    username: str
    total: float


# item of .response.topNodes[] on /api/node-plugins/torrent-blocker/stats
class TorrentBlockerTopNode(Struct):
    uuid: str
    country_code: str
    color: str
    name: str
    total: float


# .response on /api/node-plugins/torrent-blocker/stats
class TorrentBlockerStats(Struct):
    stats: TorrentBlockerStatsSummary
    top_users: list[TorrentBlockerTopUser]
    top_nodes: list[TorrentBlockerTopNode]
