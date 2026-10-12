# Security policy

mcp-otx is an independent project and is not affiliated with AlienVault, AT&T Cybersecurity or LevelBlue.

## Supported versions

Only the latest release receives security fixes.

| Version | Supported |
|---|---|
| Latest release | Yes |
| Older releases | No |

## Reporting a vulnerability

Use GitHub private vulnerability reporting. Open the repository's **Security** tab and choose **Report a vulnerability**. Do not open a public issue or pull request for a suspected vulnerability.

Include:

- The mcp-otx version or commit, and your Python version.
- The transport and mode (stdio or HTTP; read-only or `--read-write`).
- Steps to reproduce, and the expected and actual results.
- The impact you believe the issue has.

Do not include API keys, bearer tokens or indicators from private investigations in a report.

## Scope

In scope:

- **API key or bearer token leakage** in logs, error messages or tool output.
- **Read-only bypass**: any way to reach a tool or API call that changes the OTX account (create, subscribe, follow, submit) without `--read-write`.
- **HTTP transport authentication**: bypassing the bearer token check, or the refusal to bind a non-localhost address without a token or `--allow-remote`.
- **Request forgery**: tool input that changes the host or method of a request, or reaches a host other than the configured OTX API.

Out of scope:

- **OTX's API, data and pulse content.** Report these to OTX.
- **Prompt injection through community content** beyond what is documented below. Pulse and indicator descriptions are untrusted by design.
- **Local attackers with the same OS user**, who can already read the environment and `.env`.
- **Deliberately unauthenticated deployments** started with `--allow-remote`.
- **Automated scanner findings** without a working reproduction.

## Trust model

The server acts as your OTX account, using the `OTX_API_KEY` from the environment or `.env`. It sends the key only to the configured `OTX_API_BASE` (by default `https://otx.alienvault.com/api/v1`) in the `X-OTX-API-KEY` header.

- **Read-only by default.** The nine tools that change your account are not registered unless you pass `--read-write` or set `OTX_MCP_READ_WRITE=1`.
- **stdio** does not authenticate the client, which runs as the same OS user.
- **HTTP transports** (`streamable-http`, `sse`) bind to `127.0.0.1` by default. Binding any other address requires `OTX_MCP_BEARER_TOKEN` (clients must send `Authorization: Bearer <token>`; the comparison is constant-time) or an explicit `--allow-remote`. Use TLS in front of the server if the token crosses a network.
- **Untrusted content.** Pulse descriptions, indicator descriptions and whois text are written by the OTX community and reach the model's context. The server's instructions tell the model to treat them as data. Be careful combining `--read-write` with a client that acts on tool output without asking you.
