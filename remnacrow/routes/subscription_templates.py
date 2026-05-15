from typing import Any

from ..enums import SubscriptionTemplateType
from ..models.envelope import Envelope
from ..models.subscription_templates import (
    SubscriptionTemplate,
    SubscriptionTemplatesPage,
)
from .base import BaseRoute, pack


class SubscriptionTemplatesRoute(BaseRoute):
    """``/api/subscription-templates`` endpoints, mounted at
    ``RemnawaveClient.subscription_templates``"""

    async def create(
        self, name: str, template_type: SubscriptionTemplateType,
    ) -> SubscriptionTemplate:
        """
        Create a new subscription template (POST /api/subscription-templates)

        :param name: template name (2-255 chars, matches ``^[A-Za-z0-9_\\s-]+$``)
        :param template_type: which renderer this template targets — see
            :class:`~remnacrow.models.SubscriptionTemplateType`
        :return: the freshly created
            :class:`~remnacrow.models.SubscriptionTemplate`
        """
        envelope: Envelope[SubscriptionTemplate] = await self._client.request(
            "POST", "/api/subscription-templates",
            body={"name": name, "templateType": template_type},
            response_type=Envelope[SubscriptionTemplate],
        )
        return envelope.response

    async def get_templates(self) -> SubscriptionTemplatesPage:
        """
        List every subscription template (GET /api/subscription-templates)

        :return: :class:`~remnacrow.models.SubscriptionTemplatesPage` with
            ``total`` and ``templates`` ordered by view position
        """
        envelope: Envelope[SubscriptionTemplatesPage] = await self._client.request(
            "GET", "/api/subscription-templates",
            response_type=Envelope[SubscriptionTemplatesPage],
        )
        return envelope.response

    async def update(
        self,
        uuid: str,
        *,
        name: str | None = None,
        template_json: Any | None = None,
        encoded_template_yaml: str | None = None,
    ) -> SubscriptionTemplate:
        """
        Patch an existing template (PATCH /api/subscription-templates)

        Only the kwargs you pass are forwarded; ``None`` values are stripped.
        Pass ``template_json`` for JSON-based renderers (XRAY_JSON), and
        ``encoded_template_yaml`` for YAML ones (MIHOMO / STASH / CLASH /
        SINGBOX).

        :param uuid: uuid of the template to update
        :param name: new template name
        :param template_json: new JSON template body (typed as ``Any`` since
            the schema is renderer-specific)
        :param encoded_template_yaml: new YAML template body, base64-encoded
        :return: the updated :class:`~remnacrow.models.SubscriptionTemplate`
        """
        body = pack(
            uuid=uuid, name=name,
            template_json=template_json, encoded_template_yaml=encoded_template_yaml,
        )
        envelope: Envelope[SubscriptionTemplate] = await self._client.request(
            "PATCH", "/api/subscription-templates",
            body=body, response_type=Envelope[SubscriptionTemplate],
        )
        return envelope.response

    async def get_template_by_uuid(self, uuid: str) -> SubscriptionTemplate:
        """
        Fetch a single template (GET /api/subscription-templates/{uuid})

        :param uuid: uuid of the template
        :return: matching :class:`~remnacrow.models.SubscriptionTemplate`
        """
        envelope: Envelope[SubscriptionTemplate] = await self._client.request(
            "GET", f"/api/subscription-templates/{uuid}",
            response_type=Envelope[SubscriptionTemplate],
        )
        return envelope.response

    async def delete(self, uuid: str) -> bool:
        """
        Remove a template (DELETE /api/subscription-templates/{uuid})

        :param uuid: uuid of the template to delete
        :return: ``True`` if the panel removed the row (``isDeleted`` flag)
        """
        data = await self._client.request(
            "DELETE", f"/api/subscription-templates/{uuid}", response_type=dict,
        )
        return bool(data["response"]["isDeleted"])

    async def reorder(self, order: dict[str, int]) -> SubscriptionTemplatesPage:
        """
        Reorder templates in the panel
        (POST /api/subscription-templates/actions/reorder)

        :param order: mapping of template uuid → new ``view_position``
        :return: :class:`~remnacrow.models.SubscriptionTemplatesPage`
            reflecting the new positions
        """
        body = {
            "items": [
                {"uuid": template_uuid, "viewPosition": position}
                for template_uuid, position in order.items()
            ]
        }
        envelope: Envelope[SubscriptionTemplatesPage] = await self._client.request(
            "POST", "/api/subscription-templates/actions/reorder",
            body=body, response_type=Envelope[SubscriptionTemplatesPage],
        )
        return envelope.response
