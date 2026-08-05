from .base import Struct


class AuthToken(Struct):
    access_token: str


class AuthPasskeyStatus(Struct):
    enabled: bool


class AuthOAuth2Status(Struct):
    providers: dict[str, bool]


class AuthPasswordStatus(Struct):
    enabled: bool


class AuthAuthenticationStatus(Struct):
    passkey: AuthPasskeyStatus
    oauth2: AuthOAuth2Status
    password: AuthPasswordStatus


class AuthBranding(Struct):
    title: str | None
    logo_url: str | None


class AuthStatus(Struct):
    is_login_allowed: bool
    is_register_allowed: bool
    authentication: AuthAuthenticationStatus | None
    branding: AuthBranding


class OAuth2AuthorizeResult(Struct):
    authorization_url: str | None
