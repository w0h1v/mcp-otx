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


PULSE_SUMMARY_LIMIT = 10
SUMMARY_LIST_LIMIT = 10
SECTION_LIST_LIMIT = 20
REFERENCE_MAX_CHARS = 200


def _names(items: Any, keys: tuple[str, ...]) -> list[str]:
    """Reduce a list of strings or {id, name, ...} dicts to plain strings."""
    out: list[str] = []
    for item in items or []:
        if isinstance(item, dict):
            item = next((item[k] for k in keys if item.get(k)), None)
        if isinstance(item, str) and item:
            out.append(item)
        if len(out) >= SUMMARY_LIST_LIMIT:
            break
    return out


def summarize_pulse(pulse: dict[str, Any]) -> dict[str, Any]:
    """Compact view of a pulse embedded in an indicator lookup."""
    author = pulse.get("author")
    if isinstance(author, dict):
        author = author.get("username")
    adversary = pulse.get("adversary")
    summary: dict[str, Any] = {
        "id": pulse.get("id"),
        "name": pulse.get("name"),
        "author": author or pulse.get("author_name"),
        "created": pulse.get("created"),
        "modified": pulse.get("modified"),
        "TLP": pulse.get("TLP") or pulse.get("tlp"),
        "tags": [t for t in (pulse.get("tags") or []) if isinstance(t, str)][
            :SUMMARY_LIST_LIMIT
        ],
        "malware_families": _names(
            pulse.get("malware_families"), ("display_name", "id", "name")
        ),
        "adversary": [adversary] if isinstance(adversary, str) and adversary
        else _names(adversary, ("display_name", "name", "id")),
        "attack_ids": _names(pulse.get("attack_ids"), ("id", "display_name")),
        "indicator_count": pulse.get("indicator_count"),
    }
    return {k: v for k, v in summary.items() if v not in (None, "", [])}


def _shape_pulse_info(info: dict[str, Any]) -> dict[str, Any]:
    pulses = info.get("pulses")
    if isinstance(pulses, list):
        total = info.get("count", len(pulses))
        shown = [summarize_pulse(p) if isinstance(p, dict) else p
                 for p in pulses[:PULSE_SUMMARY_LIMIT]]
        info = {**info, "pulses": shown, "pulses_shown": len(shown)}
        if isinstance(total, int) and total > len(shown):
            info["note"] = (
                f"Showing {len(shown)} of {total} related pulses; use "
                "get_pulse_details for one or search_pulses for more."
            )
    refs = info.get("references")
    if isinstance(refs, list) and len(refs) > SECTION_LIST_LIMIT:
        info = {**info, "references": refs[:SECTION_LIST_LIMIT],
                "references_total": len(refs)}
    if isinstance(info.get("references"), list):
        info["references"] = [
            r[:REFERENCE_MAX_CHARS] + "..." if isinstance(r, str)
            and len(r) > REFERENCE_MAX_CHARS else r
            for r in info["references"]
        ]
    related = info.get("related")
    if isinstance(related, dict):
        info = {**info, "related": {
            src: {k: v[:SECTION_LIST_LIMIT] if isinstance(v, list) else v
                  for k, v in group.items()} if isinstance(group, dict) else group
            for src, group in related.items()
        }}
    return info


def _collect_cpes(node: Any, found: dict[str, None]) -> None:
    if isinstance(node, dict):
        for key in ("cpe23Uri", "criteria"):
            if isinstance(node.get(key), str):
                found.setdefault(node[key])
        for v in node.values():
            _collect_cpes(v, found)
    elif isinstance(node, list):
        for v in node:
            _collect_cpes(v, found)


def _shape_configurations(cfg: Any) -> Any:
    if not isinstance(cfg, dict):
        return cfg
    nodes = cfg.get("nodes")
    nodes = nodes if isinstance(nodes, list) else []
    found: dict[str, None] = {}
    _collect_cpes(nodes, found)
    cpes = list(found)
    note = "Configuration tree summarised."
    if len(cpes) > SECTION_LIST_LIMIT:
        note = f"Showing {SECTION_LIST_LIMIT} of {len(cpes)} distinct CPEs."
    return {"node_count": len(nodes), "cpe_count": len(cpes),
            "cpes": cpes[:SECTION_LIST_LIMIT], "note": note}


def _compact_entry(entry: Any, dupes: dict[str, str | None]) -> Any:
    if not isinstance(entry, dict):
        return entry
    out = {}
    for k, v in entry.items():
        if v in (None, "", []):
            continue
        if k in dupes:
            other = dupes[k]
            if other is None or (isinstance(v, str) and v.startswith(str(entry.get(other)))):
                continue
        out[k] = v
    return out


def shape_indicator_details(data: Any) -> Any:
    """Compact the bulky nested parts of an indicator detail response."""
    if not isinstance(data, dict):
        return data
    data = dict(data)
    if isinstance(data.get("pulse_info"), dict):
        data["pulse_info"] = _shape_pulse_info(data["pulse_info"])
    if "configurations" in data:
        data["configurations"] = _shape_configurations(data["configurations"])
    for key in ("exploits", "references"):
        items = data.get(key)
        if isinstance(items, list) and len(items) > SECTION_LIST_LIMIT:
            data[key] = items[:SECTION_LIST_LIMIT]
            data[f"{key}_total"] = len(items)
    # NVD reference entries repeat the URL in both `href` and `name`; exploit
    # entries repeat the date and CVE id. Drop duplicates and empty values.
    for key, dupes in (("references", {"name": "href"}),
                       ("exploits", {"published_date": "date", "cve": None})):
        items = data.get(key)
        if isinstance(items, list):
            data[key] = [_compact_entry(i, dupes) for i in items]
    return data


def strip_pulse_indicators(data: Any) -> Any:
    """Drop embedded indicator arrays from pulse list results.

    Keeps (or derives) indicator_count and points to get_pulse_indicators.
    """
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        return data
    results = []
    for pulse in data["results"]:
        if isinstance(pulse, dict) and isinstance(pulse.get("indicators"), list):
            pulse = dict(pulse)
            indicators = pulse.pop("indicators")
            if pulse.get("indicator_count") is None:
                pulse["indicator_count"] = len(indicators)
            pulse["indicators_note"] = (
                "Indicators omitted; use get_pulse_indicators for this pulse."
            )
        results.append(pulse)
    return {**data, "results": results}


__all__ = [
    "OTXAPIError",
    "ToolError",
    "deep_trim",
    "shape_indicator_details",
    "strip_pulse_indicators",
    "summarize_pulse",
]
