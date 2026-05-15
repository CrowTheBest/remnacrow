from typing import Any

from remnacrow.models import (
    Filter,
    FilterMode,
    HwidAppCount,
    HwidDevice,
    HwidDevicesPage,
    HwidDevicesStats,
    HwidField,
    HwidGlobalStats,
    HwidPlatformCount,
    HwidTopUser,
    HwidTopUsersPage,
    Sort,
)

from .conftest import BASE_URL, last_request, request_body, request_query


SAMPLE_DEVICE: dict[str, Any] = {
    "hwid": "device-abc",
    "userUuid": "11111111-2222-3333-4444-555555555555",
    "platform": "iOS",
    "osVersion": "17.4",
    "deviceModel": "iPhone 15 Pro",
    "userAgent": "Happ/1.0",
    "createdAt": "2026-05-01T12:00:00Z",
    "updatedAt": "2026-05-15T12:00:00Z",
}


async def test_get_all_devices_paginated(client, mock_api):
    url = f"{BASE_URL}/api/hwid/devices?size=50&start=10"
    mock_api.get(
        url,
        payload={"response": {"devices": [SAMPLE_DEVICE], "total": 1}},
    )

    page = await client.hwid.get_devices(size=50, start=10)

    assert isinstance(page, HwidDevicesPage)
    assert page.total == 1
    assert isinstance(page.devices[0], HwidDevice)
    assert page.devices[0].platform == "iOS"
    assert page.devices[0].os_version == "17.4"


async def test_get_all_devices_no_args_sends_defaults(client, mock_api):
    url = f"{BASE_URL}/api/hwid/devices?size=25&start=0"
    mock_api.get(url, payload={"response": {"devices": [], "total": 0}})

    await client.hwid.get_devices()
    call = last_request(mock_api, "GET", url)
    assert request_query(call) == {"size": 25, "start": 0}


async def test_create_device(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/hwid/devices",
        payload={"response": {"devices": [SAMPLE_DEVICE], "total": 1}},
    )

    page = await client.hwid.create_device(
        "device-abc",
        "11111111-2222-3333-4444-555555555555",
        platform="iOS",
        os_version="17.4",
        device_model="iPhone 15 Pro",
        user_agent="Happ/1.0",
    )

    assert page.total == 1
    call = last_request(mock_api, "POST", f"{BASE_URL}/api/hwid/devices")
    assert request_body(call) == {
        "hwid": "device-abc",
        "userUuid": "11111111-2222-3333-4444-555555555555",
        "platform": "iOS",
        "osVersion": "17.4",
        "deviceModel": "iPhone 15 Pro",
        "userAgent": "Happ/1.0",
    }


async def test_create_device_only_required_args(client, mock_api):
    """Optional metadata fields stripped when not provided"""
    mock_api.post(
        f"{BASE_URL}/api/hwid/devices",
        payload={"response": {"devices": [SAMPLE_DEVICE], "total": 1}},
    )
    await client.hwid.create_device("hw1", "user-uuid-1")

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/hwid/devices")
    assert request_body(call) == {"hwid": "hw1", "userUuid": "user-uuid-1"}


async def test_delete_device(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/hwid/devices/delete",
        payload={"response": {"devices": [], "total": 0}},
    )

    page = await client.hwid.delete_device("user-uuid-1", "hw-bad")

    assert page.total == 0
    assert page.devices == []
    call = last_request(mock_api, "POST", f"{BASE_URL}/api/hwid/devices/delete")
    assert request_body(call) == {"userUuid": "user-uuid-1", "hwid": "hw-bad"}


async def test_delete_all_devices(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/hwid/devices/delete-all",
        payload={"response": {"devices": [], "total": 0}},
    )

    page = await client.hwid.delete_all_devices("user-uuid-1")

    assert page.total == 0
    call = last_request(mock_api, "POST", f"{BASE_URL}/api/hwid/devices/delete-all")
    assert request_body(call) == {"userUuid": "user-uuid-1"}


async def test_get_devices_stats(client, mock_api):
    payload = {
        "response": {
            "byPlatform": [
                {"platform": "iOS", "count": 42},
                {"platform": "Android", "count": 30},
            ],
            "byApp": [
                {"app": "Happ", "count": 60},
                {"app": "FlClashX", "count": 12},
            ],
            "stats": {
                "totalUniqueDevices": 70,
                "totalHwidDevices": 72,
                "averageHwidDevicesPerUser": 1.5,
            },
        },
    }
    mock_api.get(f"{BASE_URL}/api/hwid/devices/stats", payload=payload)

    stats = await client.hwid.get_devices_stats()

    assert isinstance(stats, HwidDevicesStats)
    assert isinstance(stats.by_platform[0], HwidPlatformCount)
    assert stats.by_platform[0].platform == "iOS"
    assert stats.by_platform[0].count == 42
    assert isinstance(stats.by_app[0], HwidAppCount)
    assert stats.by_app[0].app == "Happ"
    assert isinstance(stats.stats, HwidGlobalStats)
    assert stats.stats.total_unique_devices == 70
    assert stats.stats.average_hwid_devices_per_user == 1.5


async def test_get_top_users(client, mock_api):
    url = f"{BASE_URL}/api/hwid/devices/top-users?size=10&start=0"
    payload = {
        "response": {
            "users": [
                {"userUuid": "u-1", "id": 1, "username": "alice", "devicesCount": 7},
                {"userUuid": "u-2", "id": 2, "username": "bob", "devicesCount": 5},
            ],
            "total": 2,
        },
    }
    mock_api.get(url, payload=payload)

    page = await client.hwid.get_top_users(size=10, start=0)

    assert isinstance(page, HwidTopUsersPage)
    assert page.total == 2
    assert isinstance(page.users[0], HwidTopUser)
    assert page.users[0].username == "alice"
    assert page.users[0].devices_count == 7


async def test_get_user_devices(client, mock_api):
    user_uuid = "11111111-2222-3333-4444-555555555555"
    mock_api.get(
        f"{BASE_URL}/api/hwid/devices/{user_uuid}",
        payload={"response": {"devices": [SAMPLE_DEVICE], "total": 1}},
    )

    page = await client.hwid.get_user_devices(user_uuid)

    assert page.total == 1
    assert page.devices[0].user_uuid == user_uuid


async def test_get_devices_with_filters_and_sort(client, mock_api):
    """Real-world panel query: filter by platform + osVersion, sort by updatedAt"""
    import re
    mock_api.get(
        re.compile(rf"^{re.escape(BASE_URL)}/api/hwid/devices(\?.*)?$"),
        payload={"response": {"devices": [SAMPLE_DEVICE], "total": 1}},
    )

    await client.hwid.get_devices(
        size=25,
        start=0,
        filters=[
            Filter(HwidField.PLATFORM, "Android"),
            Filter(HwidField.OS_VERSION, "14"),
        ],
        sort=[Sort(HwidField.UPDATED_AT)],
    )

    call = last_request(mock_api, "GET", f"{BASE_URL}/api/hwid/devices")
    query = request_query(call)
    assert query["size"] == 25
    assert query["start"] == 0

    import json as json_module
    assert json_module.loads(query["filters"]) == [
        {"id": "platform", "value": "Android"},
        {"id": "osVersion", "value": "14"},
    ]
    assert json_module.loads(query["sorting"]) == [
        {"id": "updatedAt", "desc": False},
    ]


async def test_get_devices_with_explicit_filter_mode(client, mock_api):
    """When a Filter has mode set, it shows up in filterModes"""
    import re
    mock_api.get(
        re.compile(rf"^{re.escape(BASE_URL)}/api/hwid/devices(\?.*)?$"),
        payload={"response": {"devices": [], "total": 0}},
    )

    await client.hwid.get_devices(
        filters=[Filter(HwidField.PLATFORM, "iOS", FilterMode.EQUALS)],
    )

    call = last_request(mock_api, "GET", f"{BASE_URL}/api/hwid/devices")
    import json as json_module
    assert json_module.loads(request_query(call)["filterModes"]) == {"platform": "equals"}


async def test_hwid_route_mounted_on_client(client):
    """Sanity check: every documented HWID method is callable through client.hwid"""
    expected = {
        "get_devices", "create_device", "delete_device", "delete_all_devices",
        "get_devices_stats", "get_top_users", "get_user_devices",
    }
    actual = {name for name in dir(client.hwid) if not name.startswith("_")}
    assert expected == actual, f"diff: {expected ^ actual}"
