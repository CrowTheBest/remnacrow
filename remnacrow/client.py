import atexit
import warnings
from contextlib import suppress
from typing import Any

import aiohttp
import msgspec

from .exceptions import error_for_status
from .routes import (
    ExternalSquadsRoute,
    HwidRoute,
    InternalSquadsRoute,
    NodesRoute,
    StatsRoute,
    SubscriptionPageConfigsRoute,
    SubscriptionSettingsRoute,
    SubscriptionTemplatesRoute,
    SubscriptionsRoute,
    UsersRoute,
)

DECODER_CACHE: dict[Any, msgspec.json.Decoder] = {}
ENCODER = msgspec.json.Encoder()


def _decoder(response_type: Any) -> msgspec.json.Decoder:
    decoder = DECODER_CACHE.get(response_type)
    if decoder is None:
        decoder = msgspec.json.Decoder(response_type)
        DECODER_CACHE[response_type] = decoder
    return decoder


class RemnawaveClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        timeout: float = 30.0,
    ) -> None:
        if not base_url.startswith(("http://", "https://")):
            base_url = f"https://{base_url}"

        self._base_url = base_url.rstrip("/")
        self._token = token
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: aiohttp.ClientSession | None = None

        self.users = UsersRoute(self)
        self.hwid = HwidRoute(self)
        self.nodes = NodesRoute(self)
        self.internal_squads = InternalSquadsRoute(self)
        self.external_squads = ExternalSquadsRoute(self)
        self.subscriptions = SubscriptionsRoute(self)
        self.subscription_templates = SubscriptionTemplatesRoute(self)
        self.subscription_settings = SubscriptionSettingsRoute(self)
        self.subscription_page_configs = SubscriptionPageConfigsRoute(self)
        self.stats = StatsRoute(self)

        # atexit fallback: if the user never calls `await close()`, the connector
        # still gets shut down on interpreter exit (no "Unclosed client session"
        # warning, no leaked sockets). See `_close_connector_sync`.
        atexit.register(self._close_connector_sync)

    async def __aenter__(self) -> "RemnawaveClient":
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.close()

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
        self._session = None
        # session has been awaited closed cleanly; we don't need the atexit
        # fallback to fire — drop it to allow the client to be GC'd.
        atexit.unregister(self._close_connector_sync)

    def _close_connector_sync(self) -> None:
        """Synchronously close the underlying TCP connector

        Runs from an atexit hook when the user didn't ``await close()``.
        At that point the event loop is gone, so we can't simply
        ``await session.close()``. Instead:

        1. ``connector.close()`` is a coroutine, but when no connections
           are mid-flight it completes in a single step. Driving the
           coroutine manually with ``__await__().send(None)`` finishes it
           without needing a loop (vkbottle uses the same trick).
        2. ``session.detach()`` decouples the session from its connector
           so aiohttp's session ``__del__`` doesn't emit
           "Unclosed client session".
        """
        session = self._session
        if (
            session is None
            or session.closed
            or not session.connector_owner
            or session.connector is None
            or session.connector.closed
        ):
            return

        with warnings.catch_warnings(), suppress(Exception):
            warnings.simplefilter("ignore", category=RuntimeWarning)
            session.connector.close().__await__().send(None)
        session.detach()

    def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self._timeout,
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "User-Agent": "remnacrow",
                },
            )
        return self._session

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        body: msgspec.Struct | dict[str, Any] | None = None,
        response_type: Any = None,
    ) -> Any:
        session = self._ensure_session()
        url = f"{self._base_url}{path}"
        data = ENCODER.encode(body) if body is not None else None
        headers = {"Content-Type": "application/json"} if data else None

        async with session.request(method, url, params=params, data=data, headers=headers) as response:
            raw = await response.read()

            if response.status >= 400:
                err_cls = error_for_status(response.status)
                message = ""
                error_payload: Any = None
                try:
                    if raw:
                        error_payload = msgspec.json.decode(raw)
                        if isinstance(error_payload, dict):
                            message = str(error_payload.get("message") or "")
                except msgspec.DecodeError:
                    error_payload = raw.decode("utf-8", errors="replace")
                    message = error_payload

                raise err_cls(message, status_code=response.status, payload=error_payload)

            if response_type is None or not raw:
                return None
            return _decoder(response_type).decode(raw)
