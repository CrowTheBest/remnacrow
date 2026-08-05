from datetime import datetime

from .base import Struct


class Passkey(Struct):
    id: str
    name: str
    created_at: datetime
    last_used_at: datetime


class PasskeysResult(Struct):
    passkeys: list[Passkey]


class PasskeyRegistrationResult(Struct):
    verified: bool
