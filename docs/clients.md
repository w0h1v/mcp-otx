# Connect a client

mcp-otx speaks MCP over stdio by default. Every client needs the same two things: how to start the server and the `OTX_API_KEY` environment variable ([get a key](https://otx.alienvault.com/settings/api); a free OTX account is enough).

The examples use [uv](https://docs.astral.sh/uv/)'s `uvx`, which downloads and runs the package in an isolated environment. With pip, install once with `pip install otx-mcp` and use the command `otx-mcp` instead of `uvx otx-mcp`.

!!! note "Before the first PyPI release"
    Until `otx-mcp` is on PyPI, replace `uvx otx-mcp` with `uvx --from git+https://github.com/w0h1v/mcp-otx otx-mcp`, which runs the latest code from GitHub.

## Requirements

- Python 3.10 or newer (uv installs one for you if needed).
- An OTX API key.

## Claude Code

```sh
claude mcp add --transport stdio --env OTX_API_KEY=your-key otx -- uvx otx-mcp
claude mcp get otx      # should show: Connected
```

## Codex CLI

```sh
codex mcp add otx --env OTX_API_KEY=your-key -- uvx otx-mcp
```

## Gemini CLI

```sh
gemini mcp add -e OTX_API_KEY=your-key otx uvx otx-mcp
```

## Claude Desktop

Edit the config file, then restart the app.

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

```json
{
  "mcpServers": {
    "otx": {
      "command": "uvx",
      "args": ["otx-mcp"],
      "env": { "OTX_API_KEY": "your-otx-api-key" }
    }
  }
}
```

Desktop apps may not see your shell's `PATH`. If the server doesn't start, use the absolute path to `uvx` (`which uvx`).

## VS Code (GitHub Copilot)

Create `.vscode/mcp.json` in your workspace, or add the server to your user configuration with **MCP: Add Server**, then reload VS Code.

```json
{
  "servers": {
    "otx": {
      "command": "uvx",
      "args": ["otx-mcp"],
      "env": { "OTX_API_KEY": "your-otx-api-key" }
    }
  }
}
```

## Cline

Use the same `command`/`args`/`env` as Claude Desktop in Cline's MCP settings. See `cline_mcp_settings.json.example` in the repository.

## Enabling write tools

The server is read-only by default. To let the agent create pulses, subscribe, follow users or submit URLs, add `--read-write` to the arguments (`"args": ["otx-mcp", "--read-write"]`) or set `OTX_MCP_READ_WRITE=1`. See the [security model](security.md) first.

## From source

```sh
git clone https://github.com/w0h1v/mcp-otx && cd mcp-otx
uv venv && uv pip install -e .
```

Use the command `/absolute/path/to/mcp-otx/.venv/bin/otx-mcp`. The server also reads `OTX_API_KEY` from a `.env` file in its working directory (`cp .env.example .env`).

## HTTP (streamable HTTP)

```sh
OTX_API_KEY=your-key uvx otx-mcp --transport streamable-http
# → http://127.0.0.1:8000/mcp
```

Options: `--host`, `--port`, `--json-response` (plain JSON instead of SSE streams), `--stateless-http` (a session per request), and `--transport sse` for clients that still need the legacy SSE transport.

To accept connections from other machines, set a bearer token. The server refuses to bind a non-localhost address without one unless you pass `--allow-remote`.

```sh
OTX_API_KEY=your-key OTX_MCP_BEARER_TOKEN=a-long-random-secret \
  uvx otx-mcp --transport streamable-http --host 0.0.0.0
```

Clients then send `Authorization: Bearer a-long-random-secret`. Put TLS in front of it if the token crosses a network.

### Docker

```sh
docker build -t mcp-otx .
docker run --rm -p 127.0.0.1:8000:8000 \
  -e OTX_API_KEY=your-key -e OTX_MCP_BEARER_TOKEN=a-long-random-secret \
  -e OTX_MCP_TRANSPORT=streamable-http -e OTX_MCP_HOST=0.0.0.0 mcp-otx
```

Inside the container the server must bind `0.0.0.0` to be reachable, so a bearer token is required; publishing the port on `127.0.0.1` keeps it off the network. For stdio clients, run the image with `docker run -i --rm -e OTX_API_KEY=your-key mcp-otx`.
