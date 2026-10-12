# Security model

mcp-otx acts as your OTX account. These defaults keep that safe; change them knowingly.

## Read-only by default

20 read tools are always available. The 9 tools that change your account are only registered with `--read-write` (or `OTX_MCP_READ_WRITE=1`):

| Write tool | What it does to your account |
|---|---|
| `create_pulse` | Publishes a new pulse under your name (public or private) |
| `subscribe_pulse`, `unsubscribe_pulse` | Changes which pulses feed your subscriptions |
| `subscribe_user`, `unsubscribe_user` | Changes which users' pulses feed your subscriptions |
| `follow_user`, `unfollow_user` | Changes who you follow |
| `submit_url`, `submit_urls` | Sends URLs to OTX for analysis. OTX visits them, and submissions are tied to your account |

Some account operations are not exposed as tools at all, so an agent can't call them even with `--read-write`: editing, deleting or cloning pulses, uploading files, and changing the TLP of submissions. They exist only on the Python client (`otx_mcp.api.client.OTXClient`).

## Untrusted community content

Pulse descriptions, indicator descriptions and whois text are written by anyone on OTX and flow into the model's context. Someone can write a pulse that says "subscribe to this pulse" or "visit this URL".

- The server's instructions tell the model to treat that text as data, not instructions.
- Read-only mode means a successful injection still can't change your account.
- If you enable `--read-write`, use a client that asks before calling tools, and be suspicious of write actions proposed during a research session.

## HTTP transports

| Situation | What happens |
|---|---|
| Bind `127.0.0.1` / `localhost` / `::1` (default) | Allowed without authentication |
| Bind any other address with `OTX_MCP_BEARER_TOKEN` set | Allowed; every request needs `Authorization: Bearer <token>`, otherwise `401`. The comparison is constant-time |
| Bind any other address without a token | **Refused** at startup |
| Bind any other address with `--allow-remote` and no token | Allowed with a loud warning. Anyone who can reach the port uses your OTX key |

The bearer token is sent in clear over plain HTTP. Put TLS (a reverse proxy) in front of the server if clients connect over a network.

## The API key

- Read from `OTX_API_KEY` in the environment, or from `.env` in the working directory.
- Sent only to `OTX_API_BASE` (default `https://otx.alienvault.com/api/v1`), in the `X-OTX-API-KEY` header, never in URLs.
- `.env` is git-ignored and excluded from the published package and the Docker build context.

## Reporting a vulnerability

See [SECURITY.md](https://github.com/w0h1v/mcp-otx/blob/main/SECURITY.md). Report privately through GitHub security advisories.
