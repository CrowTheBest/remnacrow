from typing import Any

from .base import Struct


# .response on Create/Update/Get/Clone subscription-page-config DTOs,
# item of .response.configs[] on list / reorder responses.
# ``config`` is opaque JSON describing the page layout — kept as
# ``Any | None`` pass-through.
class SubscriptionPageConfig(Struct):
    uuid: str
    view_position: int
    name: str
    config: Any | None = None


# .response on Get/Reorder subscription-page-configs list DTOs
class SubscriptionPageConfigsPage(Struct):
    total: int
    configs: list[SubscriptionPageConfig]
