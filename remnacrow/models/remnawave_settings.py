from .base import Struct


class RemnawavePasskeySettings(Struct):
    enabled: bool = False
    rp_id: str | None = None
    origin: str | None = None


class RemnawaveOAuth2ProviderSettings(Struct):
    enabled: bool = False
    client_id: str | None = None
    client_secret: str | None = None
    allowed_emails: list[str] = []


class RemnawaveOAuth2PocketIdSettings(Struct):
    enabled: bool = False
    client_id: str | None = None
    client_secret: str | None = None
    plain_domain: str | None = None
    allowed_emails: list[str] = []


class RemnawaveOAuth2KeycloakSettings(Struct):
    enabled: bool = False
    realm: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    frontend_domain: str | None = None
    keycloak_domain: str | None = None
    allowed_emails: list[str] = []


class RemnawaveOAuth2GenericSettings(Struct):
    enabled: bool = False
    client_id: str | None = None
    client_secret: str | None = None
    with_pkce: bool = False
    authorization_url: str | None = None
    token_url: str | None = None
    frontend_domain: str | None = None
    allowed_emails: list[str] = []


class RemnawaveOAuth2TelegramSettings(Struct):
    enabled: bool = False
    client_id: str | None = None
    client_secret: str | None = None
    allowed_ids: list[str] = []
    frontend_domain: str | None = None


class RemnawaveOAuth2Settings(Struct):
    github: RemnawaveOAuth2ProviderSettings | None = None
    pocketid: RemnawaveOAuth2PocketIdSettings | None = None
    yandex: RemnawaveOAuth2ProviderSettings | None = None
    keycloak: RemnawaveOAuth2KeycloakSettings | None = None
    generic: RemnawaveOAuth2GenericSettings | None = None
    telegram: RemnawaveOAuth2TelegramSettings | None = None


class RemnawavePasswordSettings(Struct):
    enabled: bool = False


class RemnawaveBrandingSettings(Struct):
    title: str | None = None
    logo_url: str | None = None


class RemnawaveSettings(Struct):
    passkey_settings: RemnawavePasskeySettings | None = None
    oauth2_settings: RemnawaveOAuth2Settings | None = None
    password_settings: RemnawavePasswordSettings | None = None
    branding_settings: RemnawaveBrandingSettings | None = None
