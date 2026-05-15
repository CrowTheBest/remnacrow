from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..client import RemnawaveClient


def pack(**kwargs: Any) -> dict[str, Any]:
    """Build a request body dict from kwargs:
    - drops keys whose value is None
    - converts snake_case keys to camelCase (matches Remnawave wire format)
    """
    result: dict[str, Any] = {}
    for key, value in kwargs.items():
        if value is None:
            continue

        parts = key.split("_")
        camel_key = parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:])
        result[camel_key] = value

    return result


class BaseRoute:
    def __init__(self, client: "RemnawaveClient") -> None:
        self._client = client
