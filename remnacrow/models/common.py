from .base import Struct


# .response on every DELETE endpoint (nodes, users, squads, templates, page configs)
class DeletedResult(Struct):
    is_deleted: bool


# .response on every fire-and-forget action endpoint (restart, bulk actions,
# reset-traffic, add/remove all users). ``event_sent`` only confirms the panel
# dispatched the internal event — not that the work finished.
class EventSentResult(Struct):
    event_sent: bool


# .response on every synchronous bulk endpoint under /api/users/bulk
class AffectedRowsResult(Struct):
    affected_rows: int


# .response on /api/users/tags and /api/nodes/tags
class TagsResult(Struct):
    tags: list[str]
