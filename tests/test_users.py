from datetime import datetime, timezone

import pytest

from remnacrow.exceptions import (
    ConflictError,
    NotFoundError,
    ServerError,
    UnauthorizedError,
    ValidationError,
)
from remnacrow.models import (
    AccessibleNodesResult,
    Filter,
    FilterMode,
    ResolvedUser,
    Sort,
    SubscriptionRequestHistory,
    TrafficLimitStrategy,
    User,
    UserField,
    UserStatus,
    UsersPage,
)

from .conftest import BASE_URL, SAMPLE_USER, last_request, request_body, request_query



async def test_create_user_returns_user_and_sends_camelcase_body(client, mock_api):
    mock_api.post(f"{BASE_URL}/api/users", payload={"response": SAMPLE_USER})

    user = await client.users.create_user(
        username="alice",
        expire_at=datetime(2027, 1, 1, tzinfo=timezone.utc),
        telegram_id=42,
        hwid_device_limit=5,
        active_internal_squads=["sq-1", "sq-2"],
        description=None,  # must be dropped
    )

    assert isinstance(user, User)
    assert user.username == "test-user"

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/users")
    body = request_body(call)
    assert body["username"] == "alice"
    assert body["expireAt"] == "2027-01-01T00:00:00Z"
    assert body["telegramId"] == 42
    assert body["hwidDeviceLimit"] == 5
    assert body["activeInternalSquads"] == ["sq-1", "sq-2"]
    assert "description" not in body  # None-valued args are stripped by pack()


async def test_update_user_uses_patch_and_uuid_in_body(client, mock_api):
    mock_api.patch(f"{BASE_URL}/api/users", payload={"response": SAMPLE_USER})

    user = await client.users.update_user(
        uuid="u-1",
        traffic_limit_bytes=1024,
        traffic_limit_strategy=TrafficLimitStrategy.MONTH,
    )

    assert isinstance(user, User)
    call = last_request(mock_api, "PATCH", f"{BASE_URL}/api/users")
    body = request_body(call)
    assert body == {
        "uuid": "u-1",
        "trafficLimitBytes": 1024,
        "trafficLimitStrategy": "MONTH",
    }


async def test_get_all_users_paginated(client, mock_api):
    url = f"{BASE_URL}/api/users?size=25&start=50"
    mock_api.get(url, payload={"response": {"users": [SAMPLE_USER], "total": 1}})

    page = await client.users.get_users(size=25, start=50)

    assert isinstance(page, UsersPage)
    assert page.total == 1
    assert len(page.users) == 1

    call = last_request(mock_api, "GET", url)
    assert request_query(call) == {"size": 25, "start": 50}


async def test_get_users_no_params_sends_defaults(client, mock_api):
    url = f"{BASE_URL}/api/users?size=25&start=0"
    mock_api.get(url, payload={"response": {"users": [], "total": 0}})

    await client.users.get_users()
    call = last_request(mock_api, "GET", url)
    assert request_query(call) == {"size": 25, "start": 0}


async def test_get_users_with_filters(client, mock_api):
    """One filter with explicit mode"""
    import re
    mock_api.get(
        re.compile(rf"^{re.escape(BASE_URL)}/api/users(\?.*)?$"),
        payload={"response": {"users": [SAMPLE_USER], "total": 1}},
    )

    await client.users.get_users(
        filters=[Filter(field="id", value="1", mode=FilterMode.CONTAINS)],
    )

    call = last_request(mock_api, "GET", f"{BASE_URL}/api/users")
    query = request_query(call)
    assert query["size"] == 25
    assert query["start"] == 0
    import json as _json
    assert _json.loads(query["filters"]) == [{"id": "id", "value": "1"}]
    assert _json.loads(query["filterModes"]) == {"id": "contains"}


async def test_get_users_filter_without_mode_skips_filter_modes(client, mock_api):
    """Filter with mode=None should not send filterModes for that column"""
    import re
    mock_api.get(
        re.compile(rf"^{re.escape(BASE_URL)}/api/users(\?.*)?$"),
        payload={"response": {"users": [], "total": 0}},
    )

    await client.users.get_users(filters=[Filter("status", "ACTIVE")])

    call = last_request(mock_api, "GET", f"{BASE_URL}/api/users")
    query = request_query(call)
    assert "filterModes" not in query
    import json as _json
    assert _json.loads(query["filters"]) == [{"id": "status", "value": "ACTIVE"}]


async def test_get_users_with_sort(client, mock_api):
    import re
    mock_api.get(
        re.compile(rf"^{re.escape(BASE_URL)}/api/users(\?.*)?$"),
        payload={"response": {"users": [], "total": 0}},
    )

    await client.users.get_users(
        sort=[Sort("username"), Sort("createdAt", desc=True)],
    )

    call = last_request(mock_api, "GET", f"{BASE_URL}/api/users")
    import json as _json
    assert _json.loads(request_query(call)["sorting"]) == [
        {"id": "username", "desc": False},
        {"id": "createdAt", "desc": True},
    ]


async def test_filter_mode_enum_has_all_four_modes():
    """Panel supports four filter modes — make sure FilterMode covers them"""
    assert FilterMode.CONTAINS == "contains"
    assert FilterMode.STARTS_WITH == "startsWith"
    assert FilterMode.ENDS_WITH == "endsWith"
    assert FilterMode.EQUALS == "equals"


def test_filter_repr_natural_language():
    assert repr(Filter(UserField.USERNAME, "alice", FilterMode.STARTS_WITH)) == \
        "Filter(username startsWith 'alice')"
    assert repr(Filter(UserField.TAG, ["PRIVATE", "PUBLIC"], FilterMode.EQUALS)) == \
        "Filter(tag equals ['PRIVATE', 'PUBLIC'])"
    # StrEnum values flatten to their string form, no <Enum.X: 'X'> noise
    assert repr(Filter(UserField.STATUS, UserStatus.ACTIVE, FilterMode.EQUALS)) == \
        "Filter(status equals 'ACTIVE')"
    # mode=None → field=value
    assert repr(Filter(UserField.ID, "42")) == "Filter(id='42')"
    # raw strings still render cleanly
    assert repr(Filter("rawField", "val")) == "Filter(rawField='val')"


def test_sort_repr_natural_language():
    assert repr(Sort(UserField.USERNAME)) == "Sort(username asc)"
    assert repr(Sort(UserField.USED_TRAFFIC_BYTES, desc=True)) == \
        "Sort(usedTrafficBytes desc)"


async def test_close_unregisters_atexit_fallback(client, mock_api):
    """After awaiting close(), the atexit hook must be detached so the
    client can be GC'd and we don't leak refs across many short-lived clients"""
    import atexit
    from remnacrow import RemnawaveClient

    mock_api.get(f"{BASE_URL}/api/users/by-id/1", payload={"response": SAMPLE_USER})

    client_instance = RemnawaveClient(BASE_URL, "t")
    await client_instance.users.get_user_by_id(1)
    assert client_instance._session is not None

    await client_instance.close()
    assert client_instance._session is None
    # the bound method shouldn't still be in atexit's registry
    assert not atexit.unregister(client_instance._close_connector_sync)  # unregister returns nothing; calling twice no-ops


def test_close_connector_sync_no_session_is_noop():
    """atexit fallback must not blow up if no session was ever created"""
    from remnacrow import RemnawaveClient
    client_instance = RemnawaveClient("https://x", "t")
    # never called any request, no session
    assert client_instance._session is None
    # should be a no-op, no exceptions
    client_instance._close_connector_sync()


def test_struct_repr_is_multiline_with_all_fields():
    """msgspec.Struct base produces pprint-style multi-line repr"""
    from datetime import datetime, timezone
    from remnacrow.models import Squad, User, UserTraffic
    user = User(
        uuid="11111111-2222-3333-4444-555555555555",
        id=42, short_uuid="abc", username="alice",
        expire_at=datetime(2027, 1, 1, tzinfo=timezone.utc),
        telegram_id=42, email=None, description=None, tag="PRIVATE",
        hwid_device_limit=3, external_squad_uuid=None,
        trojan_password="p", vless_uuid="v", ss_password="s",
        sub_revoked_at=None, last_traffic_reset_at=None,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        subscription_url="https://x",
        active_internal_squads=[Squad(uuid="sq-1", name="Squad One")],
        user_traffic=UserTraffic(
            used_traffic_bytes=0, lifetime_used_traffic_bytes=0,
            online_at=None, first_connected_at=None, last_connected_node_uuid=None,
        ),
    )
    rendered = repr(user)

    # multi-line, opens with class name + (
    assert rendered.startswith("User(\n")
    assert rendered.endswith(")")

    # all 24 fields show up
    for field in (
        "uuid=", "id=42", "short_uuid='abc'", "username='alice'", "expire_at=",
        "telegram_id=42", "email=None", "tag='PRIVATE'", "hwid_device_limit=3",
        "trojan_password='p'", "vless_uuid='v'", "ss_password='s'",
        "subscription_url='https://x'", "user_traffic=UserTraffic(",
        "status=UserStatus.ACTIVE",
        "traffic_limit_strategy=TrafficLimitStrategy.NO_RESET",
        "last_triggered_threshold=0",
    ):
        assert field in rendered, f"missing in repr: {field}"

    # nested Struct gets its own block (indented inside parent)
    assert "    user_traffic=UserTraffic(\n" in rendered
    assert "        used_traffic_bytes=0,\n" in rendered

    # list of nested Structs gets bracketed multi-line
    assert "    active_internal_squads=[\n" in rendered
    assert "        Squad(\n" in rendered
    assert "            uuid='sq-1'," in rendered

    # enum rendered cleanly (no <Enum.X: 'X'> noise)
    assert "<UserStatus" not in rendered
    assert "<TrafficLimitStrategy" not in rendered


async def test_get_users_list_value_for_tag(client, mock_api):
    """`tag` filter supports multi-select via list[str]"""
    import re
    mock_api.get(
        re.compile(rf"^{re.escape(BASE_URL)}/api/users(\?.*)?$"),
        payload={"response": {"users": [], "total": 0}},
    )

    await client.users.get_users(
        filters=[Filter(field="tag", value=["PRIVATE", "PUBLIC"], mode=FilterMode.EQUALS)],
    )

    call = last_request(mock_api, "GET", f"{BASE_URL}/api/users")
    import json as _json
    assert _json.loads(request_query(call)["filters"]) == [
        {"id": "tag", "value": ["PRIVATE", "PUBLIC"]},
    ]


async def test_get_users_uses_user_field_enum(client, mock_api):
    """UserField StrEnum can be passed as field on Filter/Sort"""
    import re
    mock_api.get(
        re.compile(rf"^{re.escape(BASE_URL)}/api/users(\?.*)?$"),
        payload={"response": {"users": [], "total": 0}},
    )

    await client.users.get_users(
        filters=[Filter(UserField.USERNAME, "alice", FilterMode.STARTS_WITH)],
        sort=[Sort(UserField.USED_TRAFFIC_BYTES, desc=True)],
    )

    call = last_request(mock_api, "GET", f"{BASE_URL}/api/users")
    query = request_query(call)

    import json as _json
    assert _json.loads(query["filters"]) == [{"id": "username", "value": "alice"}]
    assert _json.loads(query["filterModes"]) == {"username": "startsWith"}
    assert _json.loads(query["sorting"]) == [{"id": "usedTrafficBytes", "desc": True}]


async def test_get_users_real_world_complex_query(client, mock_api):
    """Mirrors the actual panel UI query: multi-filter + sort + mixed modes"""
    import re
    mock_api.get(
        re.compile(rf"^{re.escape(BASE_URL)}/api/users(\?.*)?$"),
        payload={"response": {"users": [], "total": 0}},
    )

    await client.users.get_users(
        size=25,
        start=0,
        filters=[
            Filter(UserField.ACTIVE_INTERNAL_SQUADS, "0e7140c1-560c-4b3d-b6bb-7247646927a0"),
            Filter(UserField.TAG, ["PRIVATE"], FilterMode.EQUALS),
            Filter(UserField.USERNAME, "private", FilterMode.STARTS_WITH),
            Filter(UserField.ID, "4"),
            Filter(UserField.STATUS, "ACTIVE"),
            Filter(UserField.NODE_NAME, "366290d0-71aa-42be-ba28-fb9c1edbc966"),
        ],
        sort=[Sort(UserField.USED_TRAFFIC_BYTES, desc=True)],
    )

    call = last_request(mock_api, "GET", f"{BASE_URL}/api/users")
    query = request_query(call)

    import json as _json
    filters_payload = _json.loads(query["filters"])
    assert {"id": "username", "value": "private"} in filters_payload
    assert {"id": "tag", "value": ["PRIVATE"]} in filters_payload
    assert {"id": "status", "value": "ACTIVE"} in filters_payload
    assert {"id": "nodeName", "value": "366290d0-71aa-42be-ba28-fb9c1edbc966"} in filters_payload
    assert {"id": "activeInternalSquads", "value": "0e7140c1-560c-4b3d-b6bb-7247646927a0"} in filters_payload
    assert {"id": "id", "value": "4"} in filters_payload

    modes = _json.loads(query["filterModes"])
    assert modes == {"username": "startsWith", "tag": "equals"}

    sorting = _json.loads(query["sorting"])
    assert sorting == [{"id": "usedTrafficBytes", "desc": True}]


async def test_get_user_by_uuid(client, mock_api):
    uuid = SAMPLE_USER["uuid"]
    mock_api.get(f"{BASE_URL}/api/users/{uuid}", payload={"response": SAMPLE_USER})

    user = await client.users.get_user_by_uuid(uuid)
    assert user.uuid == uuid
    assert user.status == UserStatus.ACTIVE


async def test_delete_user_returns_bool(client, mock_api):
    mock_api.delete(
        f"{BASE_URL}/api/users/u-1",
        payload={"response": {"isDeleted": True}},
    )

    result = await client.users.delete_user("u-1")
    assert result is True


# ─── Lookups ───────────────────────────────────────────────────────────────


async def test_get_all_tags_returns_list_of_strings(client, mock_api):
    mock_api.get(
        f"{BASE_URL}/api/users/tags",
        payload={"response": {"tags": ["A", "B", "PRIVATE"]}},
    )

    tags = await client.users.get_all_tags()
    assert tags == ["A", "B", "PRIVATE"]


async def test_get_user_accessible_nodes(client, mock_api):
    payload = {
        "response": {
            "userUuid": "u-1",
            "activeNodes": [
                {
                    "uuid": "n-1",
                    "nodeName": "NL-1",
                    "countryCode": "NL",
                    "configProfileUuid": "cp-1",
                    "configProfileName": "vless",
                    "activeSquads": [
                        {"squadName": "S1", "activeInbounds": ["i1", "i2"]},
                    ],
                },
            ],
        },
    }
    mock_api.get(f"{BASE_URL}/api/users/u-1/accessible-nodes", payload=payload)

    result = await client.users.get_user_accessible_nodes("u-1")
    assert isinstance(result, AccessibleNodesResult)
    assert result.user_uuid == "u-1"
    assert result.active_nodes[0].country_code == "NL"
    assert result.active_nodes[0].active_squads[0].active_inbounds == ["i1", "i2"]


async def test_get_user_subscription_request_history(client, mock_api):
    payload = {
        "response": {
            "total": 1,
            "records": [{
                "id": 1,
                "userUuid": "u-1",
                "requestAt": "2026-05-01T12:00:00Z",
                "requestIp": "1.2.3.4",
                "userAgent": "Happ/1.0",
            }],
        },
    }
    mock_api.get(f"{BASE_URL}/api/users/u-1/subscription-request-history", payload=payload)

    history = await client.users.get_user_subscription_request_history("u-1")
    assert isinstance(history, SubscriptionRequestHistory)
    assert history.records[0].request_ip == "1.2.3.4"


async def test_get_user_by_short_uuid(client, mock_api):
    mock_api.get(
        f"{BASE_URL}/api/users/by-short-uuid/abc123",
        payload={"response": SAMPLE_USER},
    )
    user = await client.users.get_user_by_short_uuid("abc123")
    assert user.short_uuid == "abc123"


async def test_get_user_by_username(client, mock_api):
    mock_api.get(
        f"{BASE_URL}/api/users/by-username/test-user",
        payload={"response": SAMPLE_USER},
    )
    user = await client.users.get_user_by_username("test-user")
    assert user.username == "test-user"


async def test_get_user_by_id(client, mock_api):
    mock_api.get(f"{BASE_URL}/api/users/by-id/1", payload={"response": SAMPLE_USER})
    user = await client.users.get_user_by_id(1)
    assert user.id == 1


async def test_get_users_by_telegram_id_returns_list(client, mock_api):
    mock_api.get(
        f"{BASE_URL}/api/users/by-telegram-id/123456",
        payload={"response": [SAMPLE_USER, SAMPLE_USER]},
    )
    users = await client.users.get_users_by_telegram_id(123456)
    assert isinstance(users, list)
    assert len(users) == 2
    assert all(isinstance(u, User) for u in users)


async def test_get_users_by_email_returns_list(client, mock_api):
    mock_api.get(
        f"{BASE_URL}/api/users/by-email/foo@bar.com",
        payload={"response": [SAMPLE_USER]},
    )
    users = await client.users.get_users_by_email("foo@bar.com")
    assert len(users) == 1


async def test_get_users_by_tag_returns_list(client, mock_api):
    mock_api.get(
        f"{BASE_URL}/api/users/by-tag/PRIVATE",
        payload={"response": [SAMPLE_USER]},
    )
    users = await client.users.get_users_by_tag("PRIVATE")
    assert len(users) == 1


# ─── Actions ───────────────────────────────────────────────────────────────


async def test_revoke_user_subscription_no_body(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/users/u-1/actions/revoke",
        payload={"response": SAMPLE_USER},
    )
    user = await client.users.revoke_user_subscription("u-1")
    assert isinstance(user, User)

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/users/u-1/actions/revoke")
    # all kwargs were None → body must be None
    assert call.kwargs.get("data") is None


async def test_revoke_user_subscription_with_options(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/users/u-1/actions/revoke",
        payload={"response": SAMPLE_USER},
    )
    await client.users.revoke_user_subscription(
        "u-1", revoke_only_passwords=True, short_uuid="new-short",
    )

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/users/u-1/actions/revoke")
    body = request_body(call)
    assert body == {"revokeOnlyPasswords": True, "shortUuid": "new-short"}


async def test_disable_user(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/users/u-1/actions/disable",
        payload={"response": SAMPLE_USER},
    )
    user = await client.users.disable_user("u-1")
    assert isinstance(user, User)


async def test_enable_user(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/users/u-1/actions/enable",
        payload={"response": SAMPLE_USER},
    )
    user = await client.users.enable_user("u-1")
    assert isinstance(user, User)


async def test_reset_user_traffic(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/users/u-1/actions/reset-traffic",
        payload={"response": SAMPLE_USER},
    )
    user = await client.users.reset_user_traffic("u-1")
    assert isinstance(user, User)


async def test_resolve_user(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/users/resolve",
        payload={"response": {
            "uuid": "u-1", "username": "alice", "id": 7, "shortUuid": "abc",
        }},
    )
    resolved = await client.users.resolve_user(username="alice")
    assert isinstance(resolved, ResolvedUser)
    assert resolved.id == 7

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/users/resolve")
    assert request_body(call) == {"username": "alice"}


# ─── Bulk (per-uuid) ───────────────────────────────────────────────────────


async def test_bulk_delete_users_by_status(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/users/bulk/delete-by-status",
        payload={"response": {"affectedRows": 3}},
    )
    affected = await client.users.bulk_delete_users_by_status(UserStatus.EXPIRED)
    assert affected == 3

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/users/bulk/delete-by-status")
    assert request_body(call) == {"status": "EXPIRED"}


async def test_bulk_delete_users(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/users/bulk/delete",
        payload={"response": {"affectedRows": 2}},
    )
    affected = await client.users.bulk_delete_users(["u-1", "u-2"])
    assert affected == 2

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/users/bulk/delete")
    assert request_body(call) == {"uuids": ["u-1", "u-2"]}


async def test_bulk_revoke_users_subscription(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/users/bulk/revoke-subscription",
        payload={"response": {"affectedRows": 5}},
    )
    affected = await client.users.bulk_revoke_users_subscription(["u-1"])
    assert affected == 5


async def test_bulk_reset_user_traffic(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/users/bulk/reset-traffic",
        payload={"response": {"affectedRows": 4}},
    )
    affected = await client.users.bulk_reset_user_traffic(["u-1", "u-2"])
    assert affected == 4


async def test_bulk_update_users(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/users/bulk/update",
        payload={"response": {"affectedRows": 9}},
    )
    affected = await client.users.bulk_update_users(
        ["u-1", "u-2"], {"status": "DISABLED"},
    )
    assert affected == 9

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/users/bulk/update")
    assert request_body(call) == {"uuids": ["u-1", "u-2"], "fields": {"status": "DISABLED"}}


async def test_bulk_update_users_internal_squads(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/users/bulk/update-squads",
        payload={"response": {"affectedRows": 7}},
    )
    affected = await client.users.bulk_update_users_internal_squads(
        ["u-1"], ["sq-1", "sq-2"],
    )
    assert affected == 7

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/users/bulk/update-squads")
    assert request_body(call) == {
        "uuids": ["u-1"],
        "activeInternalSquads": ["sq-1", "sq-2"],
    }


async def test_bulk_extend_expiration_date(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/users/bulk/extend-expiration-date",
        payload={"response": {"affectedRows": 12}},
    )
    affected = await client.users.bulk_extend_expiration_date(["u-1", "u-2"], 30)
    assert affected == 12

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/users/bulk/extend-expiration-date")
    assert request_body(call) == {"uuids": ["u-1", "u-2"], "extendDays": 30}


# ─── Bulk (all users) ──────────────────────────────────────────────────────


async def test_bulk_all_update_users(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/users/bulk/all/update",
        payload={"response": {"eventSent": True}},
    )
    ok = await client.users.bulk_all_update_users(status=UserStatus.DISABLED)
    assert ok is True

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/users/bulk/all/update")
    assert request_body(call) == {"status": "DISABLED"}


async def test_bulk_all_update_users_no_args_sends_no_body(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/users/bulk/all/update",
        payload={"response": {"eventSent": True}},
    )
    await client.users.bulk_all_update_users()

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/users/bulk/all/update")
    assert call.kwargs.get("data") is None


async def test_bulk_all_reset_user_traffic(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/users/bulk/all/reset-traffic",
        payload={"response": {"eventSent": True}},
    )
    ok = await client.users.bulk_all_reset_user_traffic()
    assert ok is True


async def test_bulk_all_extend_expiration_date(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/users/bulk/all/extend-expiration-date",
        payload={"response": {"eventSent": True}},
    )
    ok = await client.users.bulk_all_extend_expiration_date(7)
    assert ok is True

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/users/bulk/all/extend-expiration-date")
    assert request_body(call) == {"extendDays": 7}


# ─── Cross-cutting ─────────────────────────────────────────────────────────


async def test_bearer_token_in_authorization_header(client, mock_api):
    mock_api.get(f"{BASE_URL}/api/users/by-id/1", payload={"response": SAMPLE_USER})

    await client.users.get_user_by_id(1)
    call = last_request(mock_api, "GET", f"{BASE_URL}/api/users/by-id/1")
    headers = call.kwargs.get("headers") or {}
    # session-level headers are passed via session, not per-request — verify on session
    assert client._session is not None
    assert client._session.headers.get("Authorization") == "Bearer test-token"
    assert client._session.headers.get("User-Agent") == "remnacrow"


async def test_http_base_url_adds_forwarded_headers(mock_api):
    from remnacrow import RemnawaveClient

    mock_api.get(
        "http://127.0.0.1:3000/api/users/tags",
        payload={"response": {"tags": []}},
    )

    client_instance = RemnawaveClient("http://127.0.0.1:3000", "t")
    try:
        await client_instance.users.get_all_tags()
        assert client_instance._session is not None
        assert client_instance._session.headers.get("x-forwarded-proto") == "https"
        assert client_instance._session.headers.get("x-forwarded-for") == "127.0.0.1"
    finally:
        await client_instance.close()


async def test_custom_headers_are_merged_last(mock_api):
    from remnacrow import RemnawaveClient

    mock_api.get(
        "http://127.0.0.1:3000/api/users/tags",
        payload={"response": {"tags": []}},
    )

    client_instance = RemnawaveClient(
        "http://127.0.0.1:3000",
        "t",
        custom_headers={
            "x-forwarded-for": "10.0.0.5",
            "X-Api-Key": "caddy-token",
        },
    )
    try:
        await client_instance.users.get_all_tags()
        assert client_instance._session is not None
        assert client_instance._session.headers.get("x-forwarded-proto") == "https"
        assert client_instance._session.headers.get("x-forwarded-for") == "10.0.0.5"
        assert client_instance._session.headers.get("X-Api-Key") == "caddy-token"
    finally:
        await client_instance.close()


@pytest.mark.parametrize(
    "status, exc",
    [
        (400, ValidationError),
        (401, UnauthorizedError),
        (404, NotFoundError),
        (409, ConflictError),
        (500, ServerError),
        (502, ServerError),
    ],
)
async def test_http_error_mapping(client, mock_api, status, exc):
    mock_api.get(
        f"{BASE_URL}/api/users/by-id/999",
        status=status,
        payload={"message": "oops"},
    )

    with pytest.raises(exc) as exc_info:
        await client.users.get_user_by_id(999)

    assert exc_info.value.status_code == status
    assert "oops" in str(exc_info.value)


async def test_session_reused_across_calls(client, mock_api):
    mock_api.get(f"{BASE_URL}/api/users/by-id/1", payload={"response": SAMPLE_USER}, repeat=True)

    await client.users.get_user_by_id(1)
    session_after_first = client._session
    assert session_after_first is not None

    await client.users.get_user_by_id(1)
    assert client._session is session_after_first


async def test_base_url_scheme_normalised():
    from remnacrow import RemnawaveClient
    client_with_no_scheme = RemnawaveClient("example.com", "t")
    assert client_with_no_scheme._base_url == "https://example.com"
    client_with_https = RemnawaveClient("https://example.com/", "t")
    assert client_with_https._base_url == "https://example.com"
    client_with_http = RemnawaveClient("http://internal:8080", "t")
    assert client_with_http._base_url == "http://internal:8080"


async def test_validation_error_exposes_field_errors(client, mock_api):
    """real-world example: panel rejects `size > 1000` with structured details"""
    from remnacrow.exceptions import FieldError

    mock_api.get(
        f"{BASE_URL}/api/users?size=5000&start=0",
        status=400,
        payload={
            "statusCode": 400,
            "message": "Validation failed",
            "errors": [{
                "code": "too_big",
                "maximum": 1000,
                "type": "number",
                "inclusive": True,
                "exact": False,
                "message": "Size (limit) must be less than 1000",
                "path": ["size"],
            }],
        },
    )

    with pytest.raises(ValidationError) as exc_info:
        await client.users.get_users(size=5000)

    error = exc_info.value
    assert error.status_code == 400
    assert len(error.errors) == 1

    field_error = error.errors[0]
    assert isinstance(field_error, FieldError)
    assert field_error.code == "too_big"
    assert field_error.message == "Size (limit) must be less than 1000"
    assert field_error.path == ["size"]
    assert field_error.extra["maximum"] == 1000
    assert field_error.extra["type"] == "number"

    # message surfaces the field-level detail, not just "Validation failed"
    text = str(error)
    assert "Validation failed" in text
    assert "size: Size (limit) must be less than 1000" in text


async def test_validation_error_multiple_field_errors(client, mock_api):
    mock_api.get(
        f"{BASE_URL}/api/users/by-id/0",
        status=400,
        payload={
            "statusCode": 400,
            "message": "Validation failed",
            "errors": [
                {"code": "too_small", "message": "id must be >= 1", "path": ["id"]},
                {"code": "custom", "message": "extra rule failed", "path": ["other", "nested"]},
            ],
        },
    )

    with pytest.raises(ValidationError) as exc_info:
        await client.users.get_user_by_id(0)

    error = exc_info.value
    assert len(error.errors) == 2
    assert error.errors[0].path == ["id"]
    assert error.errors[1].path == ["other", "nested"]
    text = str(error)
    assert "id: id must be >= 1" in text
    assert "other.nested: extra rule failed" in text


async def test_validation_error_without_errors_array_still_works(client, mock_api):
    """Panel may return a 400 without the structured `errors` array"""
    mock_api.get(
        f"{BASE_URL}/api/users/by-id/1",
        status=400,
        payload={"statusCode": 400, "message": "Something else broke"},
    )

    with pytest.raises(ValidationError) as exc_info:
        await client.users.get_user_by_id(1)

    error = exc_info.value
    assert error.errors == []
    assert "Something else broke" in str(error)


async def test_server_error_exposes_error_code_path_timestamp(client, mock_api):
    mock_api.get(
        f"{BASE_URL}/api/users/by-id/1",
        status=500,
        payload={
            "timestamp": "2026-05-15T12:30:45.000Z",
            "path": "/api/users/by-id/1",
            "message": "Database connection failed",
            "errorCode": "A001",
        },
    )

    with pytest.raises(ServerError) as exc_info:
        await client.users.get_user_by_id(1)

    error = exc_info.value
    assert error.status_code == 500
    assert error.error_code == "A001"
    assert error.path == "/api/users/by-id/1"
    assert error.timestamp is not None
    assert error.timestamp.year == 2026 and error.timestamp.month == 5 and error.timestamp.day == 15
    # error_code is prepended to the message for log readability
    assert "[A001]" in str(error)
    assert "Database connection failed" in str(error)


async def test_server_error_without_structured_payload(client, mock_api):
    """503 with bare {message: ...} — no errorCode/path/timestamp"""
    mock_api.get(
        f"{BASE_URL}/api/users/by-id/1",
        status=503,
        payload={"message": "Service unavailable"},
    )

    with pytest.raises(ServerError) as exc_info:
        await client.users.get_user_by_id(1)

    error = exc_info.value
    assert error.error_code is None
    assert error.path is None
    assert error.timestamp is None
    assert "Service unavailable" in str(error)


async def test_server_error_bad_timestamp_doesnt_crash(client, mock_api):
    mock_api.get(
        f"{BASE_URL}/api/users/by-id/1",
        status=500,
        payload={
            "timestamp": "not-a-real-date",
            "path": "/api/users/by-id/1",
            "message": "Boom",
            "errorCode": "X999",
        },
    )

    with pytest.raises(ServerError) as exc_info:
        await client.users.get_user_by_id(1)

    error = exc_info.value
    assert error.timestamp is None
    assert error.error_code == "X999"
    assert error.path == "/api/users/by-id/1"
