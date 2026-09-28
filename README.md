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
| `OTX_MCP_READ_ONLY` | off | `1` registers only read tools |
| `OTX_MCP_BEARER_TOKEN` | off | Require `Authorization: Bearer <token>` on HTTP transports |

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

Options: `--json-response` (plain JSON instead of SSE streams), `--stateless-http` (session per request), and legacy `--transport sse` if a client still needs it.

**HTTP transport security.** The tools act as your OTX account, so binding them to a network interface is dangerous. Defaults protect you:

- Localhost binds (`127.0.0.1`, the default) are fine as-is.
- Binding any other host **requires** one of:
  - `OTX_MCP_BEARER_TOKEN=<secret>` — clients must send `Authorization: Bearer <secret>` or get `401`, or
  - `--allow-remote` — explicit opt-in to an unauthenticated endpoint (loudly warned).

```bash
OTX_MCP_BEARER_TOKEN=s3cret otx-mcp --transport streamable-http --host 0.0.0.0 --port 8000
# client side: pass headers={"Authorization": "Bearer s3cret"} to streamable_http_client
```

**Read-only mode.** `--read-only` (or `OTX_MCP_READ_ONLY=1`) registers only the 16 read tools and drops every tool that mutates your OTX account (`create_pulse`, `subscribe_*`, `follow_*`, `submit_url*`) — recommended when exposing the server to an LLM you don't fully control.

**Prompt-injection caveat.** OTX pulse/indicator descriptions are community-authored text that flows into the model's context. The server's instructions tell the model to treat it as data, but treat write-tool output from a read-heavy session with suspicion.

Example remote client:

```python
import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

# Long read timeouts matter: OTX endpoints like pulses/events and passive_dns
# can take 10-60s, and the default client read timeout is ~5s.
http = httpx2.AsyncClient(timeout=httpx2.Timeout(30.0, read=120.0))

async with streamable_http_client("http://127.0.0.1:8000/mcp", http_client=http) as (read, write):
    async with ClientSession(read, write, read_timeout_seconds=120.0) as session:
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
