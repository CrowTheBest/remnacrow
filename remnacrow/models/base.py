import enum

import msgspec


class Struct(msgspec.Struct, rename="camel", kw_only=True, omit_defaults=True):
    """
    Base for all Remnawave API models

    JSON wire format: camelCase. Python attribute names: snake_case
    `omit_defaults=True` keeps outgoing payloads minimal

    `__repr__` is a recursive multi-line ``pprint``-style dump of all
    fields — full output, indented for readability. Nested Structs and
    lists of Structs get their own indent level
    """

    def __repr__(self) -> str:
        return self.pretty(0)

    def pretty(self, indent: int) -> str:
        inner_pad = "    " * (indent + 1)
        outer_pad = "    " * indent
        lines = [
            f"{inner_pad}{name}={_pretty_value(getattr(self, name), indent + 1)}"
            for name in self.__struct_fields__
        ]
        return f"{type(self).__name__}(\n" + ",\n".join(lines) + f",\n{outer_pad})"


def _pretty_value(value: object, indent: int) -> str:
    if isinstance(value, Struct):
        return value.pretty(indent)

    if isinstance(value, enum.Enum):
        return f"{type(value).__name__}.{value.name}"

    if isinstance(value, list) and value and any(isinstance(item, Struct) for item in value):
        inner_pad = "    " * (indent + 1)
        outer_pad = "    " * indent
        items = ",\n".join(
            f"{inner_pad}{_pretty_value(item, indent + 1)}" for item in value
        )
        return "[\n" + items + f",\n{outer_pad}]"

    return repr(value)
