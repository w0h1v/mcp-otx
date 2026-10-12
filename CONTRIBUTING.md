# Contributing to mcp-otx

## Development setup

Requires Python 3.10 or later and [uv](https://docs.astral.sh/uv/) (pip works too).

```sh
git clone https://github.com/w0h1v/mcp-otx && cd mcp-otx
uv venv && uv pip install -e ".[dev]"
.venv/bin/python -m pytest
```

Run the server against your own MCP client with `.venv/bin/otx-mcp` and `OTX_API_KEY` set (or in `.env`).

## Checks

Before opening a pull request:

1. `pytest` passes. No API key or network is needed; `tests/conftest.py` mocks the OTX API with its real routes and response shapes.
2. If you changed an API call or a tool's output, try it against the real API with your own key, using read-only tools where you can.
3. `uvx pip-audit` is clean.

## Guidelines

- **Read-only stays the default.** A new tool that changes the OTX account must be added to `WRITE_TOOL_NAMES` in `src/otx_mcp/server.py` and registered only when `read_only` is false.
- **Keep responses context-sized.** OTX returns very large objects. Cap lists and summarize nested pulses so a single call stays well under an LLM's context (see `src/otx_mcp/tools/util.py`).
- **Treat tool input as hostile.** Path segments go through the client's escaping; don't build URLs by hand.
- **Add a test for new behaviour**, against the mock transport in `tests/conftest.py`.
- **Keep docs in step with code.** Update the README, `docs/` and `CHANGELOG.md` when tools, parameters or requirements change.
- **No secrets or private data.** Use public indicators (for example 8.8.8.8 or the EICAR hash) in code, docs, tests and issues.

## Releasing

1. Bump `__version__` in `src/otx_mcp/__init__.py` (the only place the version lives) and update `CHANGELOG.md`.
2. Merge to `main`, then create a GitHub release with tag `vX.Y.Z` matching that version.
3. The `Publish` workflow runs the tests, publishes to PyPI with trusted publishing, then updates the MCP Registry.

## Security issues

Do not open a public issue for a vulnerability. Follow [SECURITY.md](SECURITY.md).

## Code of conduct

Participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). By contributing, you agree that your contribution is licensed under the MIT license.
