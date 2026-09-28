"""Shared helpers for OTX MCP tool modules."""

from __future__ import annotations

from typing import Any

from mcp.server.mcpserver.exceptions import ToolError

from otx_mcp.api.client import OTXAPIError


def deep_trim(
    value: Any, max_list: int = 50, max_str: int = 4000, depth: int = 0
) -> Any:
    """Recursively cap list lengths and string sizes in an API response.

    OTX responses are deeply nested; some lists (pulse indicators, passive
    DNS records, pulse_info.pulses) run to thousands of entries and strings
    like whois blobs or analysis output to hundreds of KB. The API's own
    count fields are preserved so nothing is silently lost.
    """
    if depth > 8:
        return "..."
    if isinstance(value, dict):
        return {k: deep_trim(v, max_list, max_str, depth + 1) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        trimmed = [deep_trim(v, max_list, max_str, depth + 1) for v in value[:max_list]]
        if len(value) > max_list:
            trimmed.append(f"... [{len(value) - max_list} more omitted of {len(value)}]")
        return trimmed
    if isinstance(value, str) and len(value) > max_str:
        return value[:max_str] + f"... [truncated, {len(value)} chars total]"
    return value


__all__ = ["OTXAPIError", "ToolError", "deep_trim"]
