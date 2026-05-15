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

## TODO

- [ ] `client.hwid` — HWID device routes
- [ ] `client.nodes` — node management
- [ ] `client.squads` — internal / external squads
- [ ] `client.subscriptions` — subscription routes
- [ ] `client.stats` — bandwidth / system stats
- [ ] Retries and rate-limit handling
- [ ] Publish to PyPI

## License

MIT
