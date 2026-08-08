import pytest

from remnacrow.models import (
    FetchUserIpsJobResult,
    FetchUsersIpsJobResult,
    IpControlSeenIp,
)

from .conftest import BASE_URL, last_request, request_body


USER_UUID = "11111111-2222-3333-4444-555555555555"
NODE_UUID = "22222222-3333-4444-5555-666666666666"


async def test_ip_control_fetch_user_ips(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/ip-control/fetch-ips/{USER_UUID}",
        payload={"response": {"jobId": "job-user-ips"}},
    )

    job_id = await client.ip_control.fetch_user_ips(USER_UUID)
    assert job_id == "job-user-ips"

    mock_api.get(
        f"{BASE_URL}/api/ip-control/fetch-ips/result/{job_id}",
        payload={
            "response": {
                "isCompleted": True,
                "isFailed": False,
                "progress": {"total": 2, "completed": 2, "percent": 100},
                "result": {
                    "success": True,
                    "userUuid": USER_UUID,
                    "userId": "42",
                    "nodes": [
                        {
                            "nodeUuid": NODE_UUID,
                            "nodeName": "node-1",
                            "countryCode": "DE",
                            "ips": [
                                {
                                    "ip": "203.0.113.10",
                                    "lastSeen": "2026-01-01T00:00:00Z",
                                }
                            ],
                        }
                    ],
                },
            }
        },
    )

    result = await client.ip_control.get_fetch_user_ips_result(job_id)

    assert isinstance(result, FetchUserIpsJobResult)
    assert result.is_completed is True
    assert result.progress is not None
    assert result.progress.percent == 100
    assert result.result is not None
    assert result.result.user_uuid == USER_UUID
    assert result.result.user_id == "42"
    assert isinstance(result.result.nodes[0].ips[0], IpControlSeenIp)


async def test_ip_control_fetch_users_ips(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/ip-control/fetch-users-ips/{NODE_UUID}",
        payload={"response": {"jobId": "job-users-ips"}},
    )

    job_id = await client.ip_control.fetch_users_ips(NODE_UUID)
    assert job_id == "job-users-ips"

    mock_api.get(
        f"{BASE_URL}/api/ip-control/fetch-users-ips/result/{job_id}",
        payload={
            "response": {
                "isCompleted": True,
                "isFailed": False,
                "result": {
                    "success": True,
                    "nodeUuid": NODE_UUID,
                    "users": [
                        {
                            "userId": 42,
                            "ips": [
                                {
                                    "ip": "203.0.113.11",
                                    "lastSeen": "2026-01-01T01:00:00Z",
                                }
                            ],
                        }
                    ],
                },
            }
        },
    )

    result = await client.ip_control.get_fetch_users_ips_result(job_id)

    assert isinstance(result, FetchUsersIpsJobResult)
    assert result.result is not None
    assert result.result.node_uuid == NODE_UUID
    assert result.result.users[0].user_id == 42


async def test_ip_control_drop_connections_by_users(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/ip-control/drop-connections",
        payload={"response": {"eventSent": True}},
    )

    assert await client.ip_control.drop_connections(user_uuids=[USER_UUID]) is True

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/ip-control/drop-connections")
    assert request_body(call) == {
        "dropBy": {"by": "userUuids", "userUuids": [USER_UUID]},
        "targetNodes": {"target": "allNodes"},
    }


async def test_ip_control_drop_connections_by_ips_on_specific_nodes(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/ip-control/drop-connections",
        payload={"response": {"eventSent": True}},
    )

    assert await client.ip_control.drop_connections(
        ip_addresses=["203.0.113.10"],
        node_uuids=[NODE_UUID],
    ) is True

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/ip-control/drop-connections")
    assert request_body(call) == {
        "dropBy": {"by": "ipAddresses", "ipAddresses": ["203.0.113.10"]},
        "targetNodes": {"target": "specificNodes", "nodeUuids": [NODE_UUID]},
    }


async def test_ip_control_drop_connections_requires_one_drop_selector(client):
    with pytest.raises(ValueError):
        await client.ip_control.drop_connections()

    with pytest.raises(ValueError):
        await client.ip_control.drop_connections(
            user_uuids=[USER_UUID],
            ip_addresses=["203.0.113.10"],
        )


async def test_metadata_route(client, mock_api):
    user_metadata = {"plan": "vip", "flags": {"beta": True}}
    node_metadata = {"rack": "r1"}

    mock_api.get(
        f"{BASE_URL}/api/metadata/user/{USER_UUID}",
        payload={"response": {"metadata": user_metadata}},
    )
    assert await client.metadata.get_user_metadata(USER_UUID) == user_metadata

    updated_user_metadata = {**user_metadata, "note": "manual"}
    mock_api.put(
        f"{BASE_URL}/api/metadata/user/{USER_UUID}",
        payload={"response": {"metadata": updated_user_metadata}},
    )
    assert await client.metadata.upsert_user_metadata(
        USER_UUID,
        updated_user_metadata,
    ) == updated_user_metadata
    call = last_request(mock_api, "PUT", f"{BASE_URL}/api/metadata/user/{USER_UUID}")
    assert request_body(call) == {"metadata": updated_user_metadata}

    mock_api.get(
        f"{BASE_URL}/api/metadata/node/{NODE_UUID}",
        payload={"response": {"metadata": node_metadata}},
    )
    assert await client.metadata.get_node_metadata(NODE_UUID) == node_metadata

    updated_node_metadata = {**node_metadata, "region": "de"}
    mock_api.put(
        f"{BASE_URL}/api/metadata/node/{NODE_UUID}",
        payload={"response": {"metadata": updated_node_metadata}},
    )
    assert await client.metadata.upsert_node_metadata(
        NODE_UUID,
        updated_node_metadata,
    ) == updated_node_metadata
    call = last_request(mock_api, "PUT", f"{BASE_URL}/api/metadata/node/{NODE_UUID}")
    assert request_body(call) == {"metadata": updated_node_metadata}
