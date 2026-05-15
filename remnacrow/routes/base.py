import json
from typing import TYPE_CHECKING, Any

from ..models.filters import Filter, Sort

if TYPE_CHECKING:
    from ..client import RemnawaveClient


def pack(**kwargs: Any) -> dict[str, Any]:
    """
    Build a request body dict from kwargs:
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


def build_list_params(
    size: int,
    start: int,
    filters: list[Filter] | None = None,
    sort: list[Sort] | None = None,
) -> dict[str, Any]:
    """
    Build query params for a TanStack-table-style list endpoint

    Returns a dict with ``size``/``start`` plus JSON-encoded
    ``filters``/``filterModes``/``sorting`` keys when relevant.
    Used by ``users.get_users`` and ``hwid.get_devices``.
    """
    params: dict[str, Any] = {"size": size, "start": start}

    if filters:
        params["filters"] = json.dumps(
            [{"id": filter_item.field, "value": filter_item.value} for filter_item in filters]
        )
        modes = {
            filter_item.field: filter_item.mode
            for filter_item in filters
            if filter_item.mode is not None
        }
        if modes:
            params["filterModes"] = json.dumps(modes)

    if sort:
        params["sorting"] = json.dumps(
            [{"id": sort_item.field, "desc": sort_item.desc} for sort_item in sort]
        )

    return params


class BaseRoute:
    def __init__(self, client: "RemnawaveClient") -> None:
        self._client = client
