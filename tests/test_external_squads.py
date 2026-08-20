from remnacrow.models import ExternalSquad, ExternalSquadsPage

from .conftest import BASE_URL


SQUAD_UUID = "11111111-2222-3333-4444-555555555555"


def _sample_external_squad():
    return {
        "uuid": SQUAD_UUID,
        "viewPosition": 1,
        "name": "external-1",
        "info": {"membersCount": 2},
        "templates": [],
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-02T00:00:00Z",
        "subscriptionSettings": {
            "profileTitle": "Remnawave",
            "supportLink": "https://support.example",
            "profileUpdateInterval": 24,
            "isProfileWebpageUrlEnabled": True,
            "serveJsonAtBaseSubscription": False,
            "randomizeHosts": True,
        },
    }


async def test_external_squad_subscription_settings_accepts_missing_custom_remarks(
    client,
    mock_api,
):
    mock_api.get(
        f"{BASE_URL}/api/external-squads",
        payload={
            "response": {
                "total": 1,
                "externalSquads": [_sample_external_squad()],
            }
        },
    )

    page = await client.external_squads.get_squads()

    assert isinstance(page, ExternalSquadsPage)
    assert isinstance(page.external_squads[0], ExternalSquad)
    assert page.external_squads[0].subscription_settings is not None
    assert page.external_squads[0].subscription_settings.is_show_custom_remarks is False
