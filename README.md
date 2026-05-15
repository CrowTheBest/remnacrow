# remnacrow

A modern, pythonic async client for the [Remnawave](https://remna.st/) panel API. Built on **aiohttp + msgspec**, fully typed, follows Python conventions all the way down.

> [Russian README →](./README-RU.md)

> PyPI release coming soon. Until then — install straight from GitHub.

## Requirements

- **Python 3.11+** (verified on 3.11 — 3.14)

## Installation

**Linux / macOS:**

```bash
pip install --only-binary=:all: git+https://github.com/CrowTheBest/remnacrow.git
```

**Windows:**

```powershell
pip install git+https://github.com/CrowTheBest/remnacrow.git
```

**Local development** (clone + editable install with test deps):

```bash
git clone https://github.com/CrowTheBest/remnacrow.git
cd remnacrow
pip install -e ".[dev]"
pytest
```

## Quick start

```python
import asyncio
from remnacrow import RemnawaveClient

client = RemnawaveClient("admin.example.com", "your-bearer-token")

async def main():
    user = await client.users.get_user_by_id(1)
    print(user)

asyncio.run(main())
```

## Filters & sort

`client.users.get_users` and `client.hwid.get_devices` accept TanStack-table-style filters and sorting — the same query format the admin UI uses (not in the OpenAPI spec, but the panel honours it):

```python
from remnacrow.models import Filter, FilterMode, Sort, UserField, UserStatus

page = await client.users.get_users(
    filters=[
        Filter(UserField.USERNAME, "crow", FilterMode.STARTS_WITH),
        Filter(UserField.STATUS, UserStatus.ACTIVE, FilterMode.EQUALS),
        Filter(UserField.TAG, "VPN") # let the panel to deside filter mode
    ],
    sort=[Sort(UserField.USED_TRAFFIC_BYTES, desc=True)],
)
```

Same shape for HWID devices:

```python
from remnacrow.models import Filter, FilterMode, HwidField, Sort

page = await client.hwid.get_devices(
    filters=[
        # Note that FilterMode.EQUALS is case-sensitive while others are not
        Filter(HwidField.PLATFORM, "Android", FilterMode.EQUALS),
        Filter(HwidField.OS_VERSION, "14", FilterMode.STARTS_WITH),
    ],
    sort=[Sort(HwidField.UPDATED_AT, desc=True)],
)
```

Modes: `contains`, `startsWith`, `endsWith`, `equals`. Use `UserField` / `HwidField` enums for column-name autocomplete.

## TODO

- [ ] `client.squads` — internal / external squads
- [ ] `client.subscriptions` — subscription routes
- [ ] `client.stats` — bandwidth / system stats
- [ ] Retries and rate-limit handling
- [ ] Publish to PyPI

## License

MIT
