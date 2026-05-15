from typing import Any

from ..models.envelope import Envelope
from ..models.subscription_page_configs import (
    SubscriptionPageConfig,
    SubscriptionPageConfigsPage,
)
from .base import BaseRoute, pack


class SubscriptionPageConfigsRoute(BaseRoute):
    """``/api/subscription-page-configs`` endpoints, mounted at
    ``RemnawaveClient.subscription_page_configs``

    Subscription-page configs back the hosted webpage URL that lists user
    apps and their per-protocol links. Each external squad / setting can
    bind one.
    """

    async def create(self, name: str) -> SubscriptionPageConfig:
        """
        Create a new page config (POST /api/subscription-page-configs)

        The panel seeds an empty ``config`` body — fill it in via
        :meth:`update`.

        :param name: config name (2-30 chars, matches ``^[A-Za-z0-9_\\s-]+$``)
        :return: the freshly created
            :class:`~remnacrow.models.SubscriptionPageConfig`
        """
        envelope: Envelope[SubscriptionPageConfig] = await self._client.request(
            "POST", "/api/subscription-page-configs",
            body={"name": name},
            response_type=Envelope[SubscriptionPageConfig],
        )
        return envelope.response

    async def get_configs(self) -> SubscriptionPageConfigsPage:
        """
        List every page config (GET /api/subscription-page-configs)

        :return: :class:`~remnacrow.models.SubscriptionPageConfigsPage` with
            ``total`` and ``configs`` ordered by view position
        """
        envelope: Envelope[SubscriptionPageConfigsPage] = await self._client.request(
            "GET", "/api/subscription-page-configs",
            response_type=Envelope[SubscriptionPageConfigsPage],
        )
        return envelope.response

    async def update(
        self,
        uuid: str,
        *,
        name: str | None = None,
        config: Any | None = None,
    ) -> SubscriptionPageConfig:
        """
        Patch an existing page config (PATCH /api/subscription-page-configs)

        :param uuid: uuid of the config to update
        :param name: new config name
        :param config: new opaque config payload — the page-layout JSON the
            panel UI builds (passed through as-is)
        :return: the updated
            :class:`~remnacrow.models.SubscriptionPageConfig`
        """
        body = pack(uuid=uuid, name=name, config=config)
        envelope: Envelope[SubscriptionPageConfig] = await self._client.request(
            "PATCH", "/api/subscription-page-configs",
            body=body, response_type=Envelope[SubscriptionPageConfig],
        )
        return envelope.response

    async def get_config_by_uuid(self, uuid: str) -> SubscriptionPageConfig:
        """
        Fetch a single page config (GET /api/subscription-page-configs/{uuid})

        :param uuid: uuid of the config
        :return: matching :class:`~remnacrow.models.SubscriptionPageConfig`
        """
        envelope: Envelope[SubscriptionPageConfig] = await self._client.request(
            "GET", f"/api/subscription-page-configs/{uuid}",
            response_type=Envelope[SubscriptionPageConfig],
        )
        return envelope.response

    async def delete(self, uuid: str) -> bool:
        """
        Remove a page config (DELETE /api/subscription-page-configs/{uuid})

        :param uuid: uuid of the config to delete
        :return: ``True`` if the panel removed the row (``isDeleted`` flag)
        """
        data = await self._client.request(
            "DELETE", f"/api/subscription-page-configs/{uuid}", response_type=dict,
        )
        return bool(data["response"]["isDeleted"])

    async def clone(self, clone_from_uuid: str) -> SubscriptionPageConfig:
        """
        Duplicate an existing page config
        (POST /api/subscription-page-configs/actions/clone)

        :param clone_from_uuid: uuid of the source config
        :return: the freshly cloned
            :class:`~remnacrow.models.SubscriptionPageConfig`
        """
        envelope: Envelope[SubscriptionPageConfig] = await self._client.request(
            "POST", "/api/subscription-page-configs/actions/clone",
            body={"cloneFromUuid": clone_from_uuid},
            response_type=Envelope[SubscriptionPageConfig],
        )
        return envelope.response

    async def reorder(self, order: dict[str, int]) -> SubscriptionPageConfigsPage:
        """
        Reorder page configs in the panel
        (POST /api/subscription-page-configs/actions/reorder)

        :param order: mapping of config uuid → new ``view_position``
        :return: :class:`~remnacrow.models.SubscriptionPageConfigsPage`
            reflecting the new positions
        """
        body = {
            "items": [
                {"uuid": config_uuid, "viewPosition": position}
                for config_uuid, position in order.items()
            ]
        }
        envelope: Envelope[SubscriptionPageConfigsPage] = await self._client.request(
            "POST", "/api/subscription-page-configs/actions/reorder",
            body=body, response_type=Envelope[SubscriptionPageConfigsPage],
        )
        return envelope.response
