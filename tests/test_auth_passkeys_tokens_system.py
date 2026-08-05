from remnacrow import RemnawaveClient
from remnacrow.enums import ApiTokenScopeKind, OAuth2Provider
from remnacrow.models import Passkey

from .conftest import BASE_URL, last_request, request_body


async def test_auth_login_status_oauth_and_passkey_options(mock_api):
    client = RemnawaveClient(BASE_URL)
    try:
        mock_api.post(f"{BASE_URL}/api/auth/login", payload={"response": {"accessToken": "jwt"}})
        token = await client.auth.login("admin", "password")
        assert token.access_token == "jwt"
        call = last_request(mock_api, "POST", f"{BASE_URL}/api/auth/login")
        assert request_body(call) == {"username": "admin", "password": "password"}
        assert "Authorization" not in call.kwargs["headers"]

        mock_api.get(
            f"{BASE_URL}/api/auth/status",
            payload={
                "response": {
                    "isLoginAllowed": True,
                    "isRegisterAllowed": False,
                    "authentication": {
                        "passkey": {"enabled": True},
                        "oauth2": {"providers": {"github": True}},
                        "password": {"enabled": True},
                    },
                    "branding": {"title": "Remnawave", "logoUrl": None},
                }
            },
        )
        status = await client.auth.get_status()
        assert status.authentication is not None
        assert status.authentication.oauth2.providers == {"github": True}

        mock_api.post(
            f"{BASE_URL}/api/auth/oauth2/authorize",
            payload={"response": {"authorizationUrl": "https://oauth.example/auth"}},
        )
        authorize = await client.auth.oauth2_authorize(OAuth2Provider.GITHUB)
        assert authorize.authorization_url == "https://oauth.example/auth"
        call = last_request(mock_api, "POST", f"{BASE_URL}/api/auth/oauth2/authorize")
        assert request_body(call) == {"provider": "github"}

        mock_api.get(
            f"{BASE_URL}/api/auth/passkey/authentication/options",
            payload={"response": {"challenge": "abc"}},
        )
        options = await client.auth.get_passkey_authentication_options()
        assert options == {"challenge": "abc"}
    finally:
        await client.close()


async def test_passkeys_route(client, mock_api):
    payload = {
        "response": {
            "passkeys": [
                {
                    "id": "passkey-1",
                    "name": "Laptop",
                    "createdAt": "2026-01-01T00:00:00Z",
                    "lastUsedAt": "2026-01-02T00:00:00Z",
                }
            ]
        }
    }
    mock_api.get(f"{BASE_URL}/api/passkeys", payload=payload)
    passkeys = await client.passkeys.get_passkeys()
    assert isinstance(passkeys[0], Passkey)
    assert passkeys[0].name == "Laptop"

    mock_api.patch(f"{BASE_URL}/api/passkeys", payload=payload)
    await client.passkeys.update_passkey("passkey-1", "Desktop")
    call = last_request(mock_api, "PATCH", f"{BASE_URL}/api/passkeys")
    assert request_body(call) == {"id": "passkey-1", "name": "Desktop"}

    mock_api.post(
        f"{BASE_URL}/api/passkeys/registration/verify",
        payload={"response": {"verified": True}},
    )
    assert await client.passkeys.verify_registration({"id": "credential"}) is True


async def test_tokens_route(client, mock_api):
    mock_api.get(
        f"{BASE_URL}/api/tokens",
        payload={
            "response": {
                "tokens": [
                    {
                        "uuid": "token-uuid",
                        "name": "CI",
                        "expireAt": "2026-02-01T00:00:00Z",
                        "scopes": ["*"],
                        "createdAt": "2026-01-01T00:00:00Z",
                        "updatedAt": "2026-01-01T00:00:00Z",
                    }
                ],
                "docs": {"enabled": True, "scalarPath": "/scalar", "swaggerPath": "/swagger"},
            }
        },
    )
    tokens = await client.tokens.get_tokens()
    assert tokens.tokens[0].name == "CI"
    assert tokens.docs.scalar_path == "/scalar"

    mock_api.post(
        f"{BASE_URL}/api/tokens",
        payload={
            "response": {
                "uuid": "token-uuid",
                "name": "CI",
                "expireAt": "2026-02-01T00:00:00Z",
                "scopes": ["users:read"],
                "createdAt": "2026-01-01T00:00:00Z",
                "updatedAt": "2026-01-01T00:00:00Z",
                "token": "secret",
            }
        },
    )
    created = await client.tokens.create_token("CI", expires_in_days=30, scopes=["users:read"])
    assert created.token == "secret"
    call = last_request(mock_api, "POST", f"{BASE_URL}/api/tokens")
    assert request_body(call) == {"name": "CI", "expiresInDays": 30, "scopes": ["users:read"]}

    mock_api.get(
        f"{BASE_URL}/api/tokens/scopes",
        payload={
            "response": {
                "wildcard": "*",
                "resources": [
                    {
                        "resource": "users",
                        "resourceScopes": ["users:read"],
                        "endpoints": [
                            {
                                "key": "users:read",
                                "kind": "read",
                                "method": "GET",
                                "path": "/api/users",
                                "description": "List users",
                            }
                        ],
                    }
                ],
            }
        },
    )
    scopes = await client.tokens.get_scopes()
    assert scopes.resources[0].endpoints[0].kind is ApiTokenScopeKind.READ

    mock_api.delete(f"{BASE_URL}/api/tokens/token-uuid", payload={"response": True})
    assert await client.tokens.delete_token("token-uuid") is True


async def test_system_route(client, mock_api):
    mock_api.get(
        f"{BASE_URL}/api/system/health",
        payload={
            "response": {
                "runtimeMetrics": [
                    {
                        "rss": 1,
                        "heapUsed": 2,
                        "heapTotal": 3,
                        "external": 4,
                        "arrayBuffers": 5,
                        "eventLoopDelayMs": 0.1,
                        "eventLoopP99Ms": 0.2,
                        "activeHandles": 6,
                        "uptime": 7,
                        "pid": 8,
                        "timestamp": 9,
                        "instanceId": "api-1",
                        "instanceType": "backend",
                    }
                ]
            }
        },
    )
    health = await client.system.get_health()
    assert health.runtime_metrics[0].instance_id == "api-1"

    mock_api.get(
        f"{BASE_URL}/api/system/metadata",
        payload={
            "response": {
                "version": "1.0.0",
                "build": {"time": "now", "number": "42"},
                "git": {
                    "backend": {"commitSha": "abc", "branch": "main", "commitUrl": "https://git/abc"},
                    "frontend": {"commitSha": "def", "commitUrl": "https://git/def"},
                },
            }
        },
    )
    metadata = await client.system.get_metadata()
    assert metadata.git.backend.branch == "main"

    mock_api.get(
        f"{BASE_URL}/api/system/tools/x25519/generate",
        payload={"response": {"keypairs": [{"publicKey": "pub", "privateKey": "priv"}]}},
    )
    keypairs = await client.system.generate_x25519_keypairs()
    assert keypairs.keypairs[0].private_key == "priv"

    mock_api.get(f"{BASE_URL}/api/keygen", payload={"response": {"pubKey": "public"}})
    public_key = await client.system.generate_public_key()
    assert public_key.pub_key == "public"

    mock_api.post(
        f"{BASE_URL}/api/system/testers/srr-matcher",
        payload={
            "response": {
                "matched": False,
                "responseType": "BLOCK",
                "matchedRule": None,
                "inputHeaders": {"user-agent": "curl"},
                "outputHeaders": {},
            }
        },
    )
    result = await client.system.debug_srr_matcher({"version": "1", "rules": []})
    assert result.response_type == "BLOCK"
    call = last_request(mock_api, "POST", f"{BASE_URL}/api/system/testers/srr-matcher")
    assert request_body(call) == {"responseRules": {"version": "1", "rules": []}}
