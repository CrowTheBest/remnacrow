from typing import Any

import pytest

from remnacrow.enums import HostAlpn, HostSecurityLayer
from remnacrow.models import Host, HostInbound

from .conftest import BASE_URL, last_request, request_body


HOST_UUID = "11111111-2222-3333-4444-555555555555"
PROFILE_UUID = "aaaa1111-2222-3333-4444-555555555555"
INBOUND_UUID = "bbbb1111-2222-3333-4444-555555555555"

SAMPLE_HOST: dict[str, Any] = {
    "uuid": HOST_UUID,
    "viewPosition": 1,
    "remark": "main-host",
    "address": "edge.example.com",
    "port": 443,
    "path": None,
    "sni": "sni.example.com",
    "host": None,
    "alpn": "h2",
    "fingerprint": None,
    "isDisabled": False,
    "securityLayer": "TLS",
    "xhttpExtraParams": None,
    "muxParams": None,
    "sockoptParams": None,
    "finalMask": None,
    "inbound": {
        "configProfileUuid": PROFILE_UUID,
        "configProfileInboundUuid": INBOUND_UUID,
    },
    "serverDescription": None,
    "tags": ["EDGE"],
    "isHidden": False,
    "overrideSniFromAddress": False,
    "keepSniBlank": False,
    "vlessRouteId": None,
    "pinnedPeerCertSha256": None,
    "verifyPeerCertByName": None,
    "shuffleHost": False,
    "mihomoX25519": False,
    "mihomoIpVersion": None,
    "nodes": [],
    "xrayJsonTemplateUuid": None,
    "excludedInternalSquads": [],
    "excludeFromSubscriptionTypes": [],
}


async def test_create_host(client, mock_api):
    mock_api.post(f"{BASE_URL}/api/hosts", payload={"response": SAMPLE_HOST})

    host = await client.hosts.create_host(
        "main-host",
        "edge.example.com",
        443,
        PROFILE_UUID,
        INBOUND_UUID,
        sni="sni.example.com",
        alpn=HostAlpn.H2,
        security_layer=HostSecurityLayer.TLS,
        tags=["EDGE"],
    )

    assert isinstance(host, Host)
    assert isinstance(host.inbound, HostInbound)
    assert host.uuid == HOST_UUID
    assert host.alpn is HostAlpn.H2
    assert host.security_layer is HostSecurityLayer.TLS

    call = last_request(mock_api, "POST", f"{BASE_URL}/api/hosts")
    assert request_body(call) == {
        "remark": "main-host",
        "address": "edge.example.com",
        "port": 443,
        "sni": "sni.example.com",
        "alpn": "h2",
        "securityLayer": "TLS",
        "tags": ["EDGE"],
        "inbound": {
            "configProfileUuid": PROFILE_UUID,
            "configProfileInboundUuid": INBOUND_UUID,
        },
    }


async def test_get_update_and_delete_host(client, mock_api):
    mock_api.get(f"{BASE_URL}/api/hosts", payload={"response": [SAMPLE_HOST]})
    hosts = await client.hosts.get_hosts()
    assert len(hosts) == 1
    assert isinstance(hosts[0], Host)

    mock_api.get(f"{BASE_URL}/api/hosts/{HOST_UUID}", payload={"response": SAMPLE_HOST})
    host = await client.hosts.get_host_by_uuid(HOST_UUID)
    assert host.uuid == HOST_UUID

    mock_api.patch(f"{BASE_URL}/api/hosts", payload={"response": SAMPLE_HOST})
    await client.hosts.update_host(
        HOST_UUID,
        port=8443,
        config_profile_uuid=PROFILE_UUID,
        config_profile_inbound_uuid=INBOUND_UUID,
    )
    call = last_request(mock_api, "PATCH", f"{BASE_URL}/api/hosts")
    assert request_body(call) == {
        "port": 8443,
        "uuid": HOST_UUID,
        "inbound": {
            "configProfileUuid": PROFILE_UUID,
            "configProfileInboundUuid": INBOUND_UUID,
        },
    }

    mock_api.delete(
        f"{BASE_URL}/api/hosts/{HOST_UUID}",
        payload={"response": {"isDeleted": True}},
    )
    assert await client.hosts.delete_host(HOST_UUID) is True


async def test_host_tags_reorder_and_bulk_actions(client, mock_api):
    mock_api.get(
        f"{BASE_URL}/api/hosts/tags",
        payload={"response": {"tags": ["EDGE", "BACKUP"]}},
    )
    assert await client.hosts.get_all_tags() == ["EDGE", "BACKUP"]

    mock_api.post(
        f"{BASE_URL}/api/hosts/actions/reorder",
        payload={"response": {"isUpdated": True}},
    )
    assert await client.hosts.reorder_hosts({HOST_UUID: 2}) is True
    call = last_request(mock_api, "POST", f"{BASE_URL}/api/hosts/actions/reorder")
    assert request_body(call) == {
        "hosts": [{"uuid": HOST_UUID, "viewPosition": 2}],
    }

    mock_api.post(
        f"{BASE_URL}/api/hosts/bulk/delete",
        payload={"response": [SAMPLE_HOST]},
    )
    deleted = await client.hosts.bulk_delete_hosts([HOST_UUID])
    assert isinstance(deleted[0], Host)
    call = last_request(mock_api, "POST", f"{BASE_URL}/api/hosts/bulk/delete")
    assert request_body(call) == {"uuids": [HOST_UUID]}

    mock_api.post(
        f"{BASE_URL}/api/hosts/bulk/disable",
        payload={"response": [SAMPLE_HOST]},
    )
    assert len(await client.hosts.bulk_disable_hosts([HOST_UUID])) == 1

    mock_api.post(
        f"{BASE_URL}/api/hosts/bulk/enable",
        payload={"response": [SAMPLE_HOST]},
    )
    assert len(await client.hosts.bulk_enable_hosts([HOST_UUID])) == 1

    mock_api.patch(
        f"{BASE_URL}/api/hosts/bulk/update",
        payload={"response": [SAMPLE_HOST]},
    )
    await client.hosts.bulk_update_hosts(
        [HOST_UUID],
        is_disabled=True,
        nodes=["node-uuid"],
    )
    call = last_request(mock_api, "PATCH", f"{BASE_URL}/api/hosts/bulk/update")
    assert request_body(call) == {
        "isDisabled": True,
        "nodes": ["node-uuid"],
        "uuids": [HOST_UUID],
    }


async def test_host_inbound_update_requires_both_uuids(client):
    with pytest.raises(ValueError):
        await client.hosts.update_host(HOST_UUID, config_profile_uuid=PROFILE_UUID)

    with pytest.raises(ValueError):
        await client.hosts.bulk_update_hosts([HOST_UUID], config_profile_inbound_uuid=INBOUND_UUID)
