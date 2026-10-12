# Troubleshooting

## "OTX_API_KEY is not set"

The server exits at startup without a key. Set `OTX_API_KEY` in your client's `env` block, export it in the shell, or put it in `.env` in the server's working directory. Get a key from your [OTX API settings](https://otx.alienvault.com/settings/api).

## 403 errors or "Authentication required"

The key is wrong or revoked. Copy it again from the [OTX API settings](https://otx.alienvault.com/settings/api), with no spaces or quotes, then restart the client. `get_current_user` confirms which account a key belongs to.

## A tool the docs mention is missing

`create_pulse`, `subscribe_*`, `unsubscribe_*`, `follow_user`, `unfollow_user` and `submit_url*` only exist with `--read-write` (or `OTX_MCP_READ_WRITE=1`). The server prints "running READ-ONLY" to stderr at startup. See the [security model](security.md).

## Timeouts on passive DNS or subscriptions

OTX is slow on some endpoints. `passive_dns` and `pulses/subscribed` regularly take 20–60 s. The server waits up to 60 s. If your client gives up first, raise its tool timeout. For remote clients, set a long read timeout as shown in the README.

## `search_related_pulses` with `malware_family` returns nothing

The OTX API currently returns no results for the `malware_family` filter, whatever the value. `adversary` and `pulse_id` work. For malware families, use `search_pulses` with the family name.

## An old pulse has no indicators

Pulse authors and OTX expire indicators over time. `get_pulse_indicators` with `include_inactive: true` includes deactivated ones; if that's still empty, the pulse has none left.

## HTTP mode refuses to start

"refusing to bind HTTP transport to non-localhost" means you asked for a network-facing address without a bearer token. Set `OTX_MCP_BEARER_TOKEN`, or bind `127.0.0.1`. `--allow-remote` overrides the check, but then anyone who can reach the port uses your OTX account.

## HTTP clients get 401

The client must send `Authorization: Bearer <token>` with exactly the value of `OTX_MCP_BEARER_TOKEN`.

## The client doesn't list the tools

- Run `uvx otx-mcp` in a terminal. It should start and wait for input (stop it with Ctrl+C). Errors there are startup problems: a missing key, or Python below 3.10.
- Desktop clients may not inherit your shell's `PATH`. Use the absolute path to `uvx` (`which uvx`).
