from typing import Any

from remnacrow.models import (
    Node,
    NodeBulkAction,
    NodeConfigProfile,
    NodeInbound,
    NodeProvider,
    NodeSystem,
    NodeVersions,
)

from .conftest import BASE_URL, last_request, request_body


NODE_UUID = "11111111-2222-3333-4444-555555555555"
PROFILE_UUID = "aaaa1111-2222-3333-4444-555555555555"
INBOUND_UUID = "bbbb1111-2222-3333-4444-555555555555"

SAMPLE_NODE: dict[str, Any] = {
    "uuid": NODE_UUID,
    "name": "node-1",
    "address": "1.2.3.4",
    "port": 62050,
    "isConnected": True,
    "isDisabled": False,
    "isConnecting": False,
    "lastStatusChange": "2026-05-15T12:00:00Z",
    "lastStatusMessage": None,
    "isTrafficTrackingActive": True,
    "trafficResetDay": 1,
    "trafficLimitBytes": 0,
    "trafficUsedBytes": 1024,
    "notifyPercent": 80,
    "viewPosition": 0,
    "countryCode": "DE",
    "consumptionMultiplier": 1.0,
    "tags": ["EU", "BERLIN"],
    "createdAt": "2026-01-01T00:00:00Z",
    "updatedAt": "2026-05-15T00:00:00Z",
    "configProfile": {
        "activeConfigProfileUuid": PROFILE_UUID,
        "activeInbounds": [
            {
                "uuid": INBOUND_UUID,
                "profileUuid": PROFILE_UUID,
                "tag": "vless-tcp",
                "type": "vless",
                "network": "tcp",
                "security": "reality",
                "port": 443,
                "rawInbound": None,
            },
        ],
    },
    "providerUuid": None,
    "provider": None,
    "activePluginUuid": None,
    "system": None,
    "versions": None,
    "xrayUptime": 12345.6,
    "usersOnline": 7,
}


async def test_create_node_only_required(client, mock_api):
    mock_api.post(f"{BASE_URL}/api/nodes", payload={"response": SAMPLE_NODE})

    node = await client.nodes.create_node(
        "node-1", "1.2.3.4", PROFILE_UUID, [INBOUND_UUID]
    )

    assert isinstance(node, Node)
    assert node.uuid == NODE_UUID
    assert isinstance(node.config_profile, NodeConfigProfile)
    assert isinstance(node.config_profile.active_inbounds[0], NodeInbound)

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/nodes")
    assert request_body(call) == {
        "name": "node-1",
        "address": "1.2.3.4",
        "configProfile": {
            "activeConfigProfileUuid": PROFILE_UUID,
            "activeInbounds": [INBOUND_UUID],
        },
    }


async def test_create_node_full_fields(client, mock_api):
    mock_api.post(f"{BASE_URL}/api/nodes", payload={"response": SAMPLE_NODE})

    await client.nodes.create_node(
        "node-1", "1.2.3.4", PROFILE_UUID, [INBOUND_UUID],
        port=62050,
        is_traffic_tracking_active=True,
        traffic_limit_bytes=10_000_000_000,
        notify_percent=80,
        traffic_reset_day=1,
        country_code="DE",
        consumption_multiplier=1.5,
        tags=["EU"],
    )

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/nodes")
    body = request_body(call)
    assert body["port"] == 62050
    assert body["countryCode"] == "DE"
    assert body["consumptionMultiplier"] == 1.5
    assert body["tags"] == ["EU"]
    assert body["configProfile"] == {
        "activeConfigProfileUuid": PROFILE_UUID,
        "activeInbounds": [INBOUND_UUID],
    }


async def test_get_all_nodes(client, mock_api):
    mock_api.get(
        f"{BASE_URL}/api/nodes",
        payload={"response": [SAMPLE_NODE, SAMPLE_NODE]},
    )

    nodes = await client.nodes.get_nodes()

    assert len(nodes) == 2
    assert all(isinstance(node, Node) for node in nodes)
    assert nodes[0].name == "node-1"


async def test_update_node_partial(client, mock_api):
    mock_api.patch(f"{BASE_URL}/api/nodes", payload={"response": SAMPLE_NODE})

    await client.nodes.update_node(NODE_UUID, name="node-renamed", country_code="NL")

    call = last_request(mock_api, "PATCH", f"{BASE_URL}/api/nodes")
    assert request_body(call) == {
        "uuid": NODE_UUID,
        "name": "node-renamed",
        "countryCode": "NL",
    }


async def test_update_node_config_profile_pair(client, mock_api):
    """Passing config_profile_uuid + active_inbounds nests them under configProfile"""
    mock_api.patch(f"{BASE_URL}/api/nodes", payload={"response": SAMPLE_NODE})

    await client.nodes.update_node(
        NODE_UUID,
        config_profile_uuid=PROFILE_UUID,
        active_inbounds=[INBOUND_UUID],
    )

    call = last_request(mock_api, "PATCH", f"{BASE_URL}/api/nodes")
    assert request_body(call) == {
        "uuid": NODE_UUID,
        "configProfile": {
            "activeConfigProfileUuid": PROFILE_UUID,
            "activeInbounds": [INBOUND_UUID],
        },
    }


async def test_update_node_skips_partial_config_profile(client, mock_api):
    """Only one of (config_profile_uuid, active_inbounds) — don't send configProfile"""
    mock_api.patch(f"{BASE_URL}/api/nodes", payload={"response": SAMPLE_NODE})

    await client.nodes.update_node(NODE_UUID, config_profile_uuid=PROFILE_UUID)

    call = last_request(mock_api, "PATCH", f"{BASE_URL}/api/nodes")
    assert "configProfile" not in request_body(call)


async def test_get_node_by_uuid(client, mock_api):
    mock_api.get(
        f"{BASE_URL}/api/nodes/{NODE_UUID}", payload={"response": SAMPLE_NODE}
    )

    node = await client.nodes.get_node_by_uuid(NODE_UUID)

    assert isinstance(node, Node)
    assert node.uuid == NODE_UUID


async def test_delete_node(client, mock_api):
    mock_api.delete(
        f"{BASE_URL}/api/nodes/{NODE_UUID}",
        payload={"response": {"isDeleted": True}},
    )

    assert await client.nodes.delete_node(NODE_UUID) is True


async def test_reorder_nodes(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/nodes/actions/reorder",
        payload={"response": [SAMPLE_NODE]},
    )

    nodes = await client.nodes.reorder_nodes({NODE_UUID: 5})

    assert len(nodes) == 1
    assert isinstance(nodes[0], Node)

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/nodes/actions/reorder")
    assert request_body(call) == {
        "nodes": [{"uuid": NODE_UUID, "viewPosition": 5}],
    }


async def test_restart_all_nodes_no_args(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/nodes/actions/restart-all",
        payload={"response": {"eventSent": True}},
    )

    assert await client.nodes.restart_all_nodes() is True

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/nodes/actions/restart-all")
    assert request_body(call) == {}


async def test_restart_all_nodes_force(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/nodes/actions/restart-all",
        payload={"response": {"eventSent": True}},
    )

    await client.nodes.restart_all_nodes(force_restart=True)

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/nodes/actions/restart-all")
    assert request_body(call) == {"forceRestart": True}


async def test_bulk_nodes_action(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/nodes/bulk-actions",
        payload={"response": {"eventSent": True}},
    )

    assert await client.nodes.bulk_nodes_action(
        [NODE_UUID], NodeBulkAction.RESTART
    ) is True

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/nodes/bulk-actions")
    assert request_body(call) == {"uuids": [NODE_UUID], "action": "RESTART"}


async def test_bulk_profile_modification(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/nodes/bulk-actions/profile-modification",
        payload={"response": {"eventSent": True}},
    )

    result = await client.nodes.bulk_profile_modification(
        [NODE_UUID], PROFILE_UUID, [INBOUND_UUID]
    )

    assert result is True
    call = last_request(
        mock_api, "POST", f"{BASE_URL}/api/nodes/bulk-actions/profile-modification"
    )
    assert request_body(call) == {
        "uuids": [NODE_UUID],
        "configProfile": {
            "activeConfigProfileUuid": PROFILE_UUID,
            "activeInbounds": [INBOUND_UUID],
        },
    }


async def test_bulk_update_nodes(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/nodes/bulk-actions/update",
        payload={"response": {"eventSent": True}},
    )

    assert await client.nodes.bulk_update_nodes(
        [NODE_UUID], country_code="FR", tags=["EU"]
    ) is True

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/nodes/bulk-actions/update")
    assert request_body(call) == {
        "uuids": [NODE_UUID],
        "fields": {"countryCode": "FR", "tags": ["EU"]},
    }


async def test_bulk_update_nodes_empty_fields(client, mock_api):
    """No kwargs → empty fields dict (panel rejects, but the client doesn't pre-validate)"""
    mock_api.post(
        f"{BASE_URL}/api/nodes/bulk-actions/update",
        payload={"response": {"eventSent": False}},
    )

    await client.nodes.bulk_update_nodes([NODE_UUID])
    call = last_request(mock_api, "POST", f"{BASE_URL}/api/nodes/bulk-actions/update")
    assert request_body(call) == {"uuids": [NODE_UUID], "fields": {}}


async def test_get_all_tags(client, mock_api):
    mock_api.get(
        f"{BASE_URL}/api/nodes/tags",
        payload={"response": {"tags": ["EU", "ASIA", "BERLIN"]}},
    )

    tags = await client.nodes.get_all_tags()
    assert tags == ["EU", "ASIA", "BERLIN"]


async def test_disable_node(client, mock_api):
    disabled_payload = {**SAMPLE_NODE, "isDisabled": True}
    mock_api.post(
        f"{BASE_URL}/api/nodes/{NODE_UUID}/actions/disable",
        payload={"response": disabled_payload},
    )

    node = await client.nodes.disable_node(NODE_UUID)
    assert isinstance(node, Node)
    assert node.is_disabled is True


async def test_enable_node(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/nodes/{NODE_UUID}/actions/enable",
        payload={"response": SAMPLE_NODE},
    )

    node = await client.nodes.enable_node(NODE_UUID)
    assert isinstance(node, Node)
    assert node.is_disabled is False


async def test_reset_node_traffic(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/nodes/{NODE_UUID}/actions/reset-traffic",
        payload={"response": {"eventSent": True}},
    )

    assert await client.nodes.reset_node_traffic(NODE_UUID) is True


async def test_restart_node(client, mock_api):
    mock_api.post(
        f"{BASE_URL}/api/nodes/{NODE_UUID}/actions/restart",
        payload={"response": {"eventSent": True}},
    )

    assert await client.nodes.restart_node(NODE_UUID) is True


async def test_connected_node_system_block(client, mock_api):
    """Live nodes carry .system + .versions + .provider; ensure they parse"""
    payload_with_system: dict[str, Any] = {
        **SAMPLE_NODE,
        "system": {
            "info": {
                "arch": "x86_64",
                "cpus": 4,
                "cpuModel": "Intel Xeon",
                "memoryTotal": 8589934592,
                "hostname": "node-1",
                "platform": "linux",
                "release": "5.15.0",
                "type": "Linux",
                "version": "#1 SMP",
                "networkInterfaces": ["eth0"],
            },
            "stats": {
                "memoryFree": 4294967296,
                "memoryUsed": 4294967296,
                "uptime": 123456.0,
                "loadAvg": [0.5, 0.7, 0.9],
                "interface": {
                    "interface": "eth0",
                    "rxBytesPerSec": 1024.0,
                    "txBytesPerSec": 2048.0,
                    "rxTotal": 99999.0,
                    "txTotal": 88888.0,
                },
            },
        },
        "versions": {"xray": "1.8.0", "node": "20.0.0"},
        "providerUuid": "cccc1111-2222-3333-4444-555555555555",
        "provider": {
            "uuid": "cccc1111-2222-3333-4444-555555555555",
            "name": "Hetzner",
            "faviconLink": None,
            "loginUrl": "https://hetzner.com",
            "createdAt": "2026-01-01T00:00:00Z",
            "updatedAt": "2026-05-01T00:00:00Z",
        },
    }
    mock_api.get(
        f"{BASE_URL}/api/nodes/{NODE_UUID}", payload={"response": payload_with_system}
    )

    node = await client.nodes.get_node_by_uuid(NODE_UUID)

    assert isinstance(node.system, NodeSystem)
    assert node.system.info.cpus == 4
    assert node.system.stats.interface.rx_bytes_per_sec == 1024.0
    assert isinstance(node.versions, NodeVersions)
    assert node.versions.xray == "1.8.0"
    assert isinstance(node.provider, NodeProvider)
    assert node.provider.name == "Hetzner"


async def test_nodes_route_mounted_on_client(client):
    """Sanity check: every documented nodes method is callable through client.nodes"""
    expected = {
        "create_node", "get_nodes", "update_node",
        "get_node_by_uuid", "delete_node",
        "reorder_nodes", "restart_all_nodes",
        "bulk_nodes_action", "bulk_profile_modification", "bulk_update_nodes",
        "get_all_tags",
        "disable_node", "enable_node", "reset_node_traffic", "restart_node",
    }
    actual = {name for name in dir(client.nodes) if not name.startswith("_")}
    assert expected == actual, f"diff: {expected ^ actual}"
