from typing import Any

from ..enums import SubscriptionTemplateType
from .base import Struct


# .response on Create/Update/Get template DTOs, item of .response.templates[]
# on list / reorder responses
class SubscriptionTemplate(Struct):
    uuid: str
    view_position: int
    name: str
    template_type: SubscriptionTemplateType
    template_json: Any | None = None
    encoded_template_yaml: str | None = None


# .response on Get/Reorder subscription-templates list DTOs
class SubscriptionTemplatesPage(Struct):
    total: int
    templates: list[SubscriptionTemplate]
