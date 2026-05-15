from dataclasses import dataclass

from ..enums import FilterMode


@dataclass
class Filter:
    """One filter constraint for a list endpoint

    Bundles together the column to filter on, the value to match, and the
    optional match mode. Several Filters can be combined in a single call —
    the panel applies them with AND-semantics.

    On the wire each Filter becomes ``{"id": field, "value": value}``
    inside the ``filters`` query param; ``mode`` (if set) goes into the
    parallel ``filterModes`` map.

    **What can go into each field**

    ``field`` — any column name accepted by the endpoint. For
    :meth:`~remnacrow.routes.UsersRoute.get_users` use
    :class:`~remnacrow.models.UserField` to get autocomplete on all 23
    columns (including dotted paths like ``userTraffic.onlineAt``).
    Raw strings work too.

    ``value`` — string or list of strings. Since :class:`~enum.StrEnum` is
    a str subclass, you can pass enum members directly:

    * :class:`~remnacrow.models.UserStatus` for ``status``
    * :class:`~remnacrow.models.TrafficLimitStrategy` for
      ``trafficLimitStrategy``
    * raw uuid strings for ``activeInternalSquads``,
      ``externalSquadUuid``, ``nodeName`` (last-connected node)
    * a list for multi-select columns like ``tag``

    ``mode`` — one of :class:`~remnacrow.models.FilterMode`
    (``CONTAINS``, ``STARTS_WITH``, ``ENDS_WITH``, ``EQUALS``) or a raw
    string. ``None`` means "use the panel's default mode for this column".

    **Examples**

    .. code-block:: python

        from remnacrow.models import Filter, FilterMode, UserField, UserStatus\n

        # username starts with "alice"\n
        Filter(UserField.USERNAME, "alice", FilterMode.STARTS_WITH)\n

        # status is exactly ACTIVE (StrEnum value used directly)\n
        Filter(UserField.STATUS, UserStatus.ACTIVE, FilterMode.EQUALS)\n

        # tag is any of PRIVATE / PUBLIC (multi-select)\n
        Filter(UserField.TAG, ["PRIVATE", "PUBLIC"], FilterMode.EQUALS)\n

        # mode omitted — panel decides\n
        Filter(UserField.ID, "42")\n

        # raw strings still work\n
        Filter("nodeName", "366290d0-71aa-42be-ba28-fb9c1edbc966")\n

    :param field: column name to filter on. Pass a
        :class:`~remnacrow.models.UserField` for autocomplete or any raw string
    :param value: value to match. Single string OR list of strings for
        multi-select columns. StrEnum members (UserStatus,
        TrafficLimitStrategy, ...) are accepted directly
    :param mode: match mode — a :class:`~remnacrow.models.FilterMode`
        member, a raw string, or ``None`` to fall back to the panel default
    """
    field: str
    value: str | list[str]
    mode: FilterMode | str | None = None

    def __repr__(self) -> str:
        field = str(self.field)
        if isinstance(self.value, list):
            value = repr([str(v) for v in self.value])
        else:
            value = repr(str(self.value))
        if self.mode is None:
            return f"Filter({field}={value})"
        return f"Filter({field} {self.mode} {value})"


@dataclass
class Sort:
    """One sort key for a list endpoint

    Multiple Sort entries are applied left-to-right as primary/secondary
    sort keys.

    On the wire each Sort becomes ``{"id": field, "desc": desc}`` inside
    the ``sorting`` query param.

    **What can go into each field**

    ``field`` — any column name accepted by the endpoint. For
    :meth:`~remnacrow.routes.UsersRoute.get_users` use
    :class:`~remnacrow.models.UserField` for autocomplete. Raw strings
    work too.

    ``desc`` — ``True`` for descending, ``False`` (default) for ascending.

    **Examples**

    .. code-block:: python

        from remnacrow.models import Sort, UserField\n

        # biggest leechers first\n
        Sort(UserField.USED_TRAFFIC_BYTES, desc=True)\n

        # alphabetical username\n
        Sort(UserField.USERNAME)\n

        # primary by status, secondary by createdAt DESC\n
        sort = [\n
            Sort(UserField.STATUS),\n
            Sort(UserField.CREATED_AT, desc=True),\n
        ]\n

    :param field: column name to sort by. Pass a
        :class:`~remnacrow.models.UserField` for autocomplete or any raw string
    :param desc: ``True`` for descending order, ``False`` (default) for ascending
    """
    field: str
    desc: bool = False

    def __repr__(self) -> str:
        direction = "desc" if self.desc else "asc"
        return f"Sort({self.field} {direction})"
