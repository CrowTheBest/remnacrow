import json
from typing import Any

import pytest
from aioresponses import aioresponses
from yarl import URL

from remnacrow import RemnawaveClient

BASE_URL = "https://panel.test"
TOKEN = "test-token"


SAMPLE_USER: dict[str, Any] = {
    "uuid": "11111111-2222-3333-4444-555555555555",
    "id": 1,
    "shortUuid": "abc123",
    "username": "test-user",
    "status": "ACTIVE",
    "trafficLimitBytes": 0,
    "trafficLimitStrategy": "NO_RESET",
    "expireAt": "2026-12-31T00:00:00Z",
    "telegramId": 123456,
    "email": None,
    "description": None,
    "tag": None,
    "hwidDeviceLimit": 3,
    "externalSquadUuid": None,
    "trojanPassword": "trojan-pw",
    "vlessUuid": "99999999-8888-7777-6666-555555555555",
    "ssPassword": "ss-pw",
    "lastTriggeredThreshold": 0,
    "subRevokedAt": None,
    "lastTrafficResetAt": None,
    "createdAt": "2026-01-01T00:00:00Z",
    "updatedAt": "2026-05-01T00:00:00Z",
    "subscriptionUrl": "https://panel.test/sub/abc",
    "activeInternalSquads": [],
    "userTraffic": {
        "usedTrafficBytes": 0,
        "lifetimeUsedTrafficBytes": 0,
        "onlineAt": None,
        "firstConnectedAt": None,
        "lastConnectedNodeUuid": None,
    },
}


@pytest.fixture
def mock_api():
    """aiohttp mock — patches ClientSession.request so no real network is hit"""
    with aioresponses() as mocker:
        yield mocker


@pytest.fixture
async def client():
    client_instance = RemnawaveClient(BASE_URL, TOKEN)
    try:
        yield client_instance
    finally:
        await client_instance.close()


def last_request(mock_api: aioresponses, method: str, url: str):
    """Find the most recent recorded call for given method + URL path

    The URL is matched on method + host + path; query string on the recorded
    call is ignored (assert against ``request_query(call)`` separately).
    """
    method = method.upper()
    target = URL(url)
    for (recorded_method, recorded_url), calls in mock_api.requests.items():
        if recorded_method != method:
            continue
        if recorded_url.host == target.host and recorded_url.path == target.path:
            return calls[-1]
    raise AssertionError(
        f"no call recorded for {method} {url}; got {list(mock_api.requests)}"
    )


def request_body(call) -> dict[str, Any] | None:
    data = call.kwargs.get("data")
    if data is None:
        return None
    if isinstance(data, (bytes, bytearray)):
        data = data.decode()
    return json.loads(data)


def request_query(call) -> dict[str, str]:
    """Pull query params from the recorded call (aioresponses stores them in kwargs['params'])"""
    return call.kwargs.get("params") or {}
