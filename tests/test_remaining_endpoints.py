from remnacrow.models import (
    ConfigProfile,
    ConfigProfilesPage,
    InfraBillingHistoryPage,
    InfraBillingNodesPage,
    InfraProvider,
    NodePlugin,
    NodePluginsPage,
    RemnawaveSettings,
    SnippetsPage,
    TorrentBlockerReportsPage,
    UsersStreamPage,
)

from .conftest import BASE_URL, SAMPLE_USER, last_request, request_body, request_query


PROFILE_UUID = "11111111-2222-3333-4444-555555555555"
INBOUND_UUID = "22222222-3333-4444-5555-666666666666"
NODE_UUID = "33333333-4444-5555-6666-777777777777"
PLUGIN_UUID = "44444444-5555-6666-7777-888888888888"
PROVIDER_UUID = "55555555-6666-7777-8888-999999999999"
BILLING_NODE_UUID = "66666666-7777-8888-9999-aaaaaaaaaaaa"
HISTORY_UUID = "77777777-8888-9999-aaaa-bbbbbbbbbbbb"


SAMPLE_CONFIG_PROFILE = {
    "uuid": PROFILE_UUID,
    "viewPosition": 1,
    "name": "default",
    "config": {"log": {"loglevel": "warning"}},
    "inbounds": [
        {
            "uuid": INBOUND_UUID,
            "profileUuid": PROFILE_UUID,
            "tag": "vless",
            "type": "vless",
            "network": "tcp",
            "security": "reality",
            "port": 443,
            "rawInbound": {"protocol": "vless"},
        }
    ],
    "nodes": [{"uuid": NODE_UUID, "name": "node-1", "countryCode": "DE"}],
    "createdAt": "2026-01-01T00:00:00Z",
    "updatedAt": "2026-01-02T00:00:00Z",
}

SAMPLE_INBOUNDS_PAGE = {
    "total": 1,
    "inbounds": [
        {
            **SAMPLE_CONFIG_PROFILE["inbounds"][0],
            "activeSquads": ["squad-uuid"],
        }
    ],
}

SAMPLE_PLUGIN = {
    "uuid": PLUGIN_UUID,
    "viewPosition": 1,
    "name": "torrent-blocker",
    "pluginConfig": {"enabled": True},
}

SAMPLE_TORRENT_REPORTS_PAGE = {
    "records": [
        {
            "id": 1,
            "userId": 2,
            "nodeId": 3,
            "user": {"uuid": SAMPLE_USER["uuid"], "username": SAMPLE_USER["username"]},
            "node": {"uuid": NODE_UUID, "name": "node-1", "countryCode": "DE"},
            "report": {
                "actionReport": {
                    "blocked": True,
                    "ip": "203.0.113.10",
                    "blockDuration": 60,
                    "willUnblockAt": "2026-01-01T01:00:00Z",
                    "userId": "2",
                    "processedAt": "2026-01-01T00:00:00Z",
                },
                "xrayReport": {
                    "email": None,
                    "level": None,
                    "protocol": None,
                    "network": "tcp",
                    "source": "203.0.113.10",
                    "destination": "example.com:443",
                    "routeTarget": None,
                    "originalTarget": None,
                    "inboundTag": None,
                    "inboundName": None,
                    "inboundLocal": None,
                    "outboundTag": None,
                    "ts": 123456,
                },
            },
            "createdAt": "2026-01-01T00:00:00Z",
        }
    ],
    "total": 1,
}

SAMPLE_PROVIDER = {
    "uuid": PROVIDER_UUID,
    "name": "provider-1",
    "faviconLink": None,
    "loginUrl": "https://provider.example",
    "createdAt": "2026-01-01T00:00:00Z",
    "updatedAt": "2026-01-02T00:00:00Z",
    "billingHistory": {"totalAmount": 12.5, "totalBills": 1},
    "billingNodes": [
        {
            "name": "node-1",
            "details": {"nodeUuid": NODE_UUID, "countryCode": "DE"},
        }
    ],
}

SAMPLE_HISTORY_PAGE = {
    "records": [
        {
            "uuid": HISTORY_UUID,
            "providerUuid": PROVIDER_UUID,
            "amount": 12.5,
            "billedAt": "2026-01-15T00:00:00Z",
            "provider": {
                "uuid": PROVIDER_UUID,
                "name": "provider-1",
                "faviconLink": None,
            },
        }
    ],
    "total": 1,
}

SAMPLE_BILLING_NODES_PAGE = {
    "totalBillingNodes": 1,
    "billingNodes": [
        {
            "uuid": BILLING_NODE_UUID,
            "nodeUuid": NODE_UUID,
            "name": None,
            "providerUuid": PROVIDER_UUID,
            "provider": {
                "uuid": PROVIDER_UUID,
                "name": "provider-1",
                "loginUrl": "https://provider.example",
                "faviconLink": None,
            },
            "node": {"uuid": NODE_UUID, "name": "node-1", "countryCode": "DE"},
            "nextBillingAt": "2026-02-01T00:00:00Z",
            "createdAt": "2026-01-01T00:00:00Z",
            "updatedAt": "2026-01-02T00:00:00Z",
        }
    ],
    "availableBillingNodes": [{"uuid": NODE_UUID, "name": "node-1", "countryCode": "DE"}],
    "totalAvailableBillingNodes": 1,
    "stats": {"upcomingNodesCount": 1, "currentMonthPayments": 12.5, "totalSpent": 99.9},
}


async def test_remnawave_settings_route(client, mock_api):
    settings = {
        "passkeySettings": {"enabled": True, "rpId": "panel.test", "origin": "https://panel.test"},
        "oauth2Settings": {
            "github": {
                "enabled": True,
                "clientId": "client-id",
                "clientSecret": "secret",
                "allowedEmails": ["admin@example.com"],
            }
        },
        "passwordSettings": {"enabled": True},
        "brandingSettings": {"title": "Remnawave", "logoUrl": None},
    }
    mock_api.get(f"{BASE_URL}/api/remnawave-settings", payload={"response": settings})
    result = await client.remnawave_settings.get_settings()
    assert isinstance(result, RemnawaveSettings)
    assert result.oauth2_settings is not None
    assert result.oauth2_settings.github is not None
    assert result.oauth2_settings.github.allowed_emails == ["admin@example.com"]

    mock_api.patch(f"{BASE_URL}/api/remnawave-settings", payload={"response": settings})
    await client.remnawave_settings.update_settings(branding_settings={"title": "New"})
    call = last_request(mock_api, "PATCH", f"{BASE_URL}/api/remnawave-settings")
    assert request_body(call) == {"brandingSettings": {"title": "New"}}


async def test_users_stream_public_subscription_and_nodes_users_usage(client, mock_api):
    mock_api.get(
        f"{BASE_URL}/api/users/stream?cursor=cursor-1&size=10",
        payload={"response": {"users": [SAMPLE_USER], "nextCursor": "next", "hasMore": True}},
    )
    users = await client.users.get_users_stream(size=10, cursor="cursor-1")
    assert isinstance(users, UsersStreamPage)
    assert users.users[0].uuid == SAMPLE_USER["uuid"]
    call = last_request(mock_api, "GET", f"{BASE_URL}/api/users/stream")
    assert request_query(call) == {"size": 10, "cursor": "cursor-1"}

    sub_info = {
        "isFound": True,
        "user": {
            "shortUuid": "short",
            "daysLeft": 10,
            "trafficUsed": "1 GB",
            "trafficLimit": "10 GB",
            "lifetimeTrafficUsed": "2 GB",
            "trafficUsedBytes": "1000",
            "trafficLimitBytes": "10000",
            "lifetimeTrafficUsedBytes": "2000",
            "username": "test-user",
            "expiresAt": "2026-12-31T00:00:00Z",
            "isActive": True,
            "userStatus": "ACTIVE",
            "trafficLimitStrategy": "NO_RESET",
        },
        "links": ["vless://one"],
        "ssConfLinks": {"one": "ss://one"},
        "subscriptionUrl": "https://panel.test/api/sub/short",
    }
    mock_api.get(f"{BASE_URL}/api/sub/short/info", payload={"response": sub_info})
    assert (await client.subscriptions.get_public_subscription_info("short")).is_found is True

    mock_api.get(f"{BASE_URL}/api/sub/short", body="vless://plain")
    assert await client.subscriptions.get_public_subscription("short") == "vless://plain"

    mock_api.get(f"{BASE_URL}/api/sub/short/mihomo", body="proxies: []")
    assert await client.subscriptions.get_public_subscription_by_client_type("short", "mihomo") == "proxies: []"

    mock_api.post(
        f"{BASE_URL}/api/bandwidth-stats/nodes/users?end=2026-01-31&start=2026-01-01&topUsersLimit=5",
        payload={
            "response": {
                "categories": ["2026-01-01"],
                "sparklineData": [1],
                "topUsers": [{"color": "#fff", "username": "test-user", "total": 1}],
            }
        },
    )
    usage = await client.stats.get_nodes_users_usage(
        [NODE_UUID],
        top_users_limit=5,
        start="2026-01-01",
        end="2026-01-31",
    )
    assert usage.top_users[0].username == "test-user"
    call = last_request(mock_api, "POST", f"{BASE_URL}/api/bandwidth-stats/nodes/users")
    assert request_query(call) == {"topUsersLimit": 5, "start": "2026-01-01", "end": "2026-01-31"}
    assert request_body(call) == {"nodesUuids": [NODE_UUID]}


async def test_config_profiles_route(client, mock_api):
    page_payload = {"total": 1, "configProfiles": [SAMPLE_CONFIG_PROFILE]}

    mock_api.get(f"{BASE_URL}/api/config-profiles", payload={"response": page_payload})
    page = await client.config_profiles.get_config_profiles()
    assert isinstance(page, ConfigProfilesPage)

    mock_api.post(f"{BASE_URL}/api/config-profiles", payload={"response": SAMPLE_CONFIG_PROFILE})
    profile = await client.config_profiles.create_config_profile("default", {"log": {}})
    assert isinstance(profile, ConfigProfile)
    call = last_request(mock_api, "POST", f"{BASE_URL}/api/config-profiles")
    assert request_body(call) == {"name": "default", "config": {"log": {}}}

    mock_api.patch(f"{BASE_URL}/api/config-profiles", payload={"response": SAMPLE_CONFIG_PROFILE})
    await client.config_profiles.update_config_profile(PROFILE_UUID, name="renamed")
    call = last_request(mock_api, "PATCH", f"{BASE_URL}/api/config-profiles")
    assert request_body(call) == {"uuid": PROFILE_UUID, "name": "renamed"}

    mock_api.get(f"{BASE_URL}/api/config-profiles/inbounds", payload={"response": SAMPLE_INBOUNDS_PAGE})
    assert (await client.config_profiles.get_all_inbounds()).inbounds[0].active_squads == ["squad-uuid"]

    mock_api.get(
        f"{BASE_URL}/api/config-profiles/{PROFILE_UUID}/inbounds",
        payload={"response": SAMPLE_INBOUNDS_PAGE},
    )
    assert (await client.config_profiles.get_inbounds_by_profile_uuid(PROFILE_UUID)).total == 1

    mock_api.get(f"{BASE_URL}/api/config-profiles/{PROFILE_UUID}", payload={"response": SAMPLE_CONFIG_PROFILE})
    assert (await client.config_profiles.get_config_profile_by_uuid(PROFILE_UUID)).uuid == PROFILE_UUID

    mock_api.get(
        f"{BASE_URL}/api/config-profiles/{PROFILE_UUID}/computed-config",
        payload={"response": SAMPLE_CONFIG_PROFILE},
    )
    assert (await client.config_profiles.get_computed_config_profile_by_uuid(PROFILE_UUID)).name == "default"

    mock_api.post(f"{BASE_URL}/api/config-profiles/actions/reorder", payload={"response": page_payload})
    await client.config_profiles.reorder_config_profiles({PROFILE_UUID: 2})
    call = last_request(mock_api, "POST", f"{BASE_URL}/api/config-profiles/actions/reorder")
    assert request_body(call) == {"items": [{"uuid": PROFILE_UUID, "viewPosition": 2}]}

    mock_api.delete(
        f"{BASE_URL}/api/config-profiles/{PROFILE_UUID}",
        payload={"response": {"isDeleted": True}},
    )
    assert await client.config_profiles.delete_config_profile(PROFILE_UUID) is True


async def test_snippets_route(client, mock_api):
    page = {"total": 1, "snippets": [{"name": "base", "snippet": {"dns": []}}]}

    mock_api.get(f"{BASE_URL}/api/snippets", payload={"response": page})
    assert isinstance(await client.snippets.get_snippets(), SnippetsPage)

    mock_api.post(f"{BASE_URL}/api/snippets", payload={"response": page})
    await client.snippets.create_snippet("base", [{"dns": []}])
    call = last_request(mock_api, "POST", f"{BASE_URL}/api/snippets")
    assert request_body(call) == {"name": "base", "snippet": [{"dns": []}]}

    mock_api.patch(f"{BASE_URL}/api/snippets", payload={"response": page})
    await client.snippets.update_snippet("base", [{"routing": {}}])
    call = last_request(mock_api, "PATCH", f"{BASE_URL}/api/snippets")
    assert request_body(call) == {"name": "base", "snippet": [{"routing": {}}]}

    mock_api.delete(f"{BASE_URL}/api/snippets", payload={"response": page})
    await client.snippets.delete_snippet("base")
    call = last_request(mock_api, "DELETE", f"{BASE_URL}/api/snippets")
    assert request_body(call) == {"name": "base"}


async def test_node_plugins_route(client, mock_api):
    page = {"total": 1, "nodePlugins": [SAMPLE_PLUGIN]}

    mock_api.get(f"{BASE_URL}/api/node-plugins", payload={"response": page})
    assert isinstance(await client.node_plugins.get_plugins(), NodePluginsPage)

    mock_api.post(f"{BASE_URL}/api/node-plugins", payload={"response": SAMPLE_PLUGIN})
    assert isinstance(await client.node_plugins.create_plugin("torrent-blocker"), NodePlugin)

    mock_api.patch(f"{BASE_URL}/api/node-plugins", payload={"response": SAMPLE_PLUGIN})
    await client.node_plugins.update_plugin(PLUGIN_UUID, plugin_config={"enabled": False})
    call = last_request(mock_api, "PATCH", f"{BASE_URL}/api/node-plugins")
    assert request_body(call) == {"uuid": PLUGIN_UUID, "pluginConfig": {"enabled": False}}

    mock_api.get(f"{BASE_URL}/api/node-plugins/{PLUGIN_UUID}", payload={"response": SAMPLE_PLUGIN})
    assert (await client.node_plugins.get_plugin_by_uuid(PLUGIN_UUID)).uuid == PLUGIN_UUID

    mock_api.post(f"{BASE_URL}/api/node-plugins/actions/reorder", payload={"response": page})
    await client.node_plugins.reorder_plugins({PLUGIN_UUID: 3})
    call = last_request(mock_api, "POST", f"{BASE_URL}/api/node-plugins/actions/reorder")
    assert request_body(call) == {"items": [{"uuid": PLUGIN_UUID, "viewPosition": 3}]}

    mock_api.post(f"{BASE_URL}/api/node-plugins/actions/clone", payload={"response": SAMPLE_PLUGIN})
    await client.node_plugins.clone_plugin(PLUGIN_UUID)
    call = last_request(mock_api, "POST", f"{BASE_URL}/api/node-plugins/actions/clone")
    assert request_body(call) == {"cloneFromUuid": PLUGIN_UUID}

    mock_api.post(f"{BASE_URL}/api/node-plugins/executor", payload={"response": {"eventSent": True}})
    assert await client.node_plugins.execute_command(
        {"command": "unblockIps", "ips": ["203.0.113.10"]},
        node_uuids=[NODE_UUID],
    ) is True
    call = last_request(mock_api, "POST", f"{BASE_URL}/api/node-plugins/executor")
    assert request_body(call) == {
        "command": {"command": "unblockIps", "ips": ["203.0.113.10"]},
        "targetNodes": {"target": "specificNodes", "nodeUuids": [NODE_UUID]},
    }

    mock_api.get(
        f"{BASE_URL}/api/node-plugins/torrent-blocker?size=10&start=20",
        payload={"response": SAMPLE_TORRENT_REPORTS_PAGE},
    )
    reports = await client.node_plugins.get_torrent_blocker_reports(size=10, start=20)
    assert isinstance(reports, TorrentBlockerReportsPage)
    call = last_request(mock_api, "GET", f"{BASE_URL}/api/node-plugins/torrent-blocker")
    assert request_query(call) == {"size": 10, "start": 20}

    mock_api.delete(
        f"{BASE_URL}/api/node-plugins/torrent-blocker/truncate",
        payload={"response": SAMPLE_TORRENT_REPORTS_PAGE},
    )
    assert (await client.node_plugins.truncate_torrent_blocker_reports()).total == 1

    mock_api.delete(
        f"{BASE_URL}/api/node-plugins/{PLUGIN_UUID}",
        payload={"response": {"isDeleted": True}},
    )
    assert await client.node_plugins.delete_plugin(PLUGIN_UUID) is True


async def test_infra_billing_route(client, mock_api):
    providers_page = {"total": 1, "providers": [SAMPLE_PROVIDER]}

    mock_api.get(f"{BASE_URL}/api/infra-billing/providers", payload={"response": providers_page})
    assert (await client.infra_billing.get_providers()).providers[0].uuid == PROVIDER_UUID

    mock_api.post(f"{BASE_URL}/api/infra-billing/providers", payload={"response": SAMPLE_PROVIDER})
    assert isinstance(await client.infra_billing.create_provider("provider-1"), InfraProvider)

    mock_api.patch(f"{BASE_URL}/api/infra-billing/providers", payload={"response": SAMPLE_PROVIDER})
    await client.infra_billing.update_provider(PROVIDER_UUID, name="provider-2")
    call = last_request(mock_api, "PATCH", f"{BASE_URL}/api/infra-billing/providers")
    assert request_body(call) == {"uuid": PROVIDER_UUID, "name": "provider-2"}

    mock_api.get(
        f"{BASE_URL}/api/infra-billing/providers/{PROVIDER_UUID}",
        payload={"response": SAMPLE_PROVIDER},
    )
    assert (await client.infra_billing.get_provider_by_uuid(PROVIDER_UUID)).name == "provider-1"

    mock_api.post(f"{BASE_URL}/api/infra-billing/history", payload={"response": SAMPLE_HISTORY_PAGE})
    assert isinstance(
        await client.infra_billing.create_history_record(
            PROVIDER_UUID,
            12.5,
            "2026-01-15T00:00:00Z",
        ),
        InfraBillingHistoryPage,
    )

    mock_api.get(f"{BASE_URL}/api/infra-billing/history", payload={"response": SAMPLE_HISTORY_PAGE})
    assert (await client.infra_billing.get_history_records()).records[0].amount == 12.5

    mock_api.get(f"{BASE_URL}/api/infra-billing/nodes", payload={"response": SAMPLE_BILLING_NODES_PAGE})
    assert isinstance(await client.infra_billing.get_nodes(), InfraBillingNodesPage)

    mock_api.patch(f"{BASE_URL}/api/infra-billing/nodes", payload={"response": SAMPLE_BILLING_NODES_PAGE})
    await client.infra_billing.update_nodes([BILLING_NODE_UUID], "2026-02-01T00:00:00Z")
    call = last_request(mock_api, "PATCH", f"{BASE_URL}/api/infra-billing/nodes")
    assert request_body(call) == {
        "uuids": [BILLING_NODE_UUID],
        "nextBillingAt": "2026-02-01T00:00:00Z",
    }

    mock_api.post(f"{BASE_URL}/api/infra-billing/nodes", payload={"response": SAMPLE_BILLING_NODES_PAGE})
    await client.infra_billing.create_node(
        PROVIDER_UUID,
        "2026-02-01T00:00:00Z",
        node_uuid=NODE_UUID,
    )
    call = last_request(mock_api, "POST", f"{BASE_URL}/api/infra-billing/nodes")
    assert request_body(call) == {
        "providerUuid": PROVIDER_UUID,
        "nodeUuid": NODE_UUID,
        "name": None,
        "nextBillingAt": "2026-02-01T00:00:00Z",
    }

    mock_api.delete(
        f"{BASE_URL}/api/infra-billing/providers/{PROVIDER_UUID}",
        payload={"response": {"isDeleted": True}},
    )
    assert await client.infra_billing.delete_provider(PROVIDER_UUID) is True

    mock_api.delete(
        f"{BASE_URL}/api/infra-billing/history/{HISTORY_UUID}",
        payload={"response": {"isDeleted": True}},
    )
    assert await client.infra_billing.delete_history_record(HISTORY_UUID) is True

    mock_api.delete(
        f"{BASE_URL}/api/infra-billing/nodes/{BILLING_NODE_UUID}",
        payload={"response": {"isDeleted": True}},
    )
    assert await client.infra_billing.delete_node(BILLING_NODE_UUID) is True
