# otx-mcp

An [MCP](https://modelcontextprotocol.io) server for [AlienVault OTX](https://otx.alienvault.com) (Open Threat Exchange, now LevelBlue) threat intelligence — full API coverage, stdio **and** streamable HTTP transports, built on the MCP Python SDK 2.x.

## What you get

**25 tools** covering the OTX DirectConnect API v1:

| Area | Tools |
| --- | --- |
| Search | `search_pulses`, `search_users` |
| Pulses | `get_pulse_details`, `get_pulse_indicators`, `list_subscribed_pulses`, `list_pulse_activity`, `get_pulse_events`, `create_pulse`, `subscribe_pulse`, `unsubscribe_pulse` |
| Indicators | `get_indicator_details`, `validate_indicator`, `list_indicator_types`, `export_indicators` |
| Users | `get_user`, `list_user_pulses`, `list_my_pulses`, `subscribe_user`, `unsubscribe_user`, `follow_user`, `unfollow_user` |
| Submissions | `submit_url`, `submit_urls`, `list_submitted_urls`, `list_submitted_files` |

**2 resource templates**: `otx://pulse/{pulse_id}` and `otx://indicator/{type}/{value}`.

`get_indicator_details` is the workhorse — every OTX indicator type and detail section in one call:

| Type | Sections |
| --- | --- |
| `IPv4`, `IPv6` | `general`, `geo`, `reputation`, `url_list`, `passive_dns`, `malware`, `nids_list`, `http_scans` |
| `domain`, `hostname` | `general`, `geo`, `url_list`, `passive_dns`, `malware`, `whois`, `http_scans` |
| `file` (MD5/SHA1/SHA256/PEHASH/IMPHASH) | `general`, `analysis` (sandbox) |
| `url` | `general`, `url_list`, `http_scans`, `screenshot` |
| `cve` | `general`, `nids_list`, `malware` |

All tools return structured JSON. Long lists are capped at 50 entries with the API's own counts preserved, so responses stay context-window friendly.

### API coverage notes

- Destructive account operations (`edit_pulse`, `delete_pulse`, `clone_pulse`, `submit_file` binary upload) are implemented on `otx_mcp.api.client.OTXClient` but **not** exposed as MCP tools, so an LLM can't delete or rewrite your pulses by accident. Call the client directly from Python if you need them.
- The OTX API is slow on some endpoints (`passive_dns`, `pulses/subscribed` regularly take 20–60 s); the client uses a 60 s timeout.

## Installation

Requires Python 3.10+.

```bash
uv venv && source .venv/bin/activate   # or: python -m venv .venv
uv pip install -e .                    # or: pip install -e .
```

## Configuration

Get an API key from your [OTX settings page](https://otx.alienvault.com/settings/api) (free account required), then:

```bash
cp .env.example .env   # and put your key in it
```

| Variable | Default | Purpose |
| --- | --- | --- |
| `OTX_API_KEY` | — | **Required.** OTX API key |
| `OTX_API_BASE` | `https://otx.alienvault.com/api/v1` | API root (override for testing) |
| `OTX_MCP_TRANSPORT` | `stdio` | Default transport: `stdio`, `streamable-http`, `sse` |
| `OTX_MCP_HOST` | `127.0.0.1` | HTTP bind host |
| `OTX_MCP_PORT` | `8000` | HTTP bind port |

## Running

### stdio (Claude Desktop, Cline, Claude Code, ...)

```bash
otx-mcp                          # or: python -m otx_mcp
otx-mcp --transport stdio        # explicit
```

Client configuration (Claude Desktop `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "otx": {
      "command": "/abs/path/to/mcp-otx/.venv/bin/otx-mcp",
      "env": { "OTX_API_KEY": "your_api_key_here" }
    }
  }
}
```

### Streamable HTTP (remote/web clients)

```bash
otx-mcp --transport streamable-http --host 127.0.0.1 --port 8000
# → http://127.0.0.1:8000/mcp
```

Options: `--json-response` (plain JSON instead of SSE streams), `--stateless-http` (session per request), and legacy `--transport sse` if a client still needs it. There is no built-in auth on the HTTP endpoint — bind to localhost or front it with a proxy if the host is shared.

Example remote client:

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async with streamable_http_client("http://127.0.0.1:8000/mcp") as (read, write, _):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool(
            "get_indicator_details",
            {"indicator_type": "IPv4", "indicator_value": "8.8.8.8", "section": "reputation"},
        )
```

## Development

```bash
uv pip install -e ".[dev]"
pytest                  # unit tests against a mocked OTX API
```

The mock transport in `tests/conftest.py` mirrors the live API's routes and response shapes; endpoint paths and per-type sections were verified against `https://otx.alienvault.com/api`.

## License

MIT
