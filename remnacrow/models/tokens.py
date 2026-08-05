from datetime import datetime

from ..enums import ApiTokenScopeKind
from .base import Struct


class ApiToken(Struct):
    uuid: str
    name: str
    expire_at: datetime
    scopes: list[str]
    created_at: datetime
    updated_at: datetime


class ApiTokenWithSecret(ApiToken):
    token: str


class ApiTokenDocs(Struct):
    enabled: bool
    scalar_path: str | None
    swagger_path: str | None


class ApiTokensResult(Struct):
    tokens: list[ApiToken]
    docs: ApiTokenDocs


class ApiTokenScopeEndpoint(Struct):
    key: str
    kind: ApiTokenScopeKind
    method: str
    path: str
    description: str


class ApiTokenScopeResource(Struct):
    resource: str
    resource_scopes: list[str]
    endpoints: list[ApiTokenScopeEndpoint]


class ApiTokenScopes(Struct):
    wildcard: str
    resources: list[ApiTokenScopeResource]
