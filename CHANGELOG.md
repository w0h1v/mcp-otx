# Changelog

## 1.2.0 (2026-10-12)

### Added
- Published to PyPI as `otx-mcp` (run with `uvx otx-mcp`) and listed on the MCP Registry as `io.github.w0h1v/otx`, both from a release workflow using trusted publishing.
- Dockerfile (non-root, stdio by default, HTTP with a bearer token).
- CI on Python 3.10–3.13 with package build checks, `pip-audit` and a Docker build; Dependabot.
- Documentation site at <https://w0h1v.github.io/mcp-otx/> with client setup, tool reference with real sample output, example workflows, security model and troubleshooting.
- LICENSE file (MIT), security policy, contributing guide, code of conduct, citation file, issue and pull request templates.

### Fixed
- `get_indicator_details` (section `general`) could return over 200,000 characters, because each related pulse came back in full. Related pulses are now summarized and capped at 10. CVE configurations become a list of affected CPEs with their version ranges, kept separate from platform CPEs (`vulnerable: false`). Exploits and references are trimmed, and total counts are kept.
- Pulse list tools no longer embed every pulse's indicators; they report `indicator_count` and point to `get_pulse_indicators`.

### Changed
- The bearer token check on HTTP transports uses a constant-time comparison.
- The version lives only in `src/otx_mcp/__init__.py`.
- Requires `mcp` 2.3 or later.
- `search_related_pulses` notes that OTX's `malware_family` filter currently returns no results.

## 1.1.0

- Complete OTX DirectConnect API coverage (29 tools), read-only mode by default, hardened HTTP transports with bearer-token auth and a refusal to bind non-localhost addresses without it.

## 1.0.0

- Initial release.
