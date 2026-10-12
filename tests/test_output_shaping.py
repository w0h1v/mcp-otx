"""Output shaping: tool results must stay LLM-context sized.

Fixtures in tests/fixtures are trimmed copies of live OTX responses.
"""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from otx_mcp.api.client import OTXClient
from otx_mcp.server import create_server

FIX = Path(__file__).parent / "fixtures"


def load(name: str):
    return json.loads((FIX / name).read_text())


def make_server(routes: dict[str, object]):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path in routes:
            return httpx.Response(200, json=routes[request.url.path])
        return httpx.Response(404, json={"detail": "nope"})

    c = OTXClient("k", "https://otx.test/api/v1")
    c._client = httpx.AsyncClient(
        base_url=c.api_base, transport=httpx.MockTransport(handler)
    )
    return create_server(client=c, read_only=False)


def size(data) -> int:
    return len(json.dumps(data))


async def call(server, name, args):
    result = await server.call_tool(name, args)
    assert not result.is_error
    return result.structured_content


FILE_PATH = "/api/v1/indicators/file/abc/general"
CVE_PATH = "/api/v1/indicators/cve/CVE-2021-44228/general"


async def test_file_general_pulses_summarised():
    raw = load("file_general.json")
    server = make_server({FILE_PATH: raw})
    out = await call(server, "get_indicator_details",
                     {"indicator_type": "file", "indicator_value": "abc"})
    pi = out["pulse_info"]
    assert pi["count"] == 50
    assert len(pi["pulses"]) == 10
    assert pi["pulses_shown"] == 10
    assert "10 of 50" in pi["note"] and "get_pulse_details" in pi["note"]
    p, src = pi["pulses"][0], raw["pulse_info"]["pulses"][0]
    assert set(p) <= {"id", "name", "author", "created", "modified", "TLP", "tags",
                      "malware_families", "adversary", "attack_ids", "indicator_count"}
    assert p["id"] == src["id"] and p["name"] == src["name"]
    assert p["author"] == src["author"]["username"]
    assert p["TLP"] == src["TLP"]
    assert p["indicator_count"] == src["indicator_count"]
    assert len(p["tags"]) <= 10
    assert all(isinstance(x, str) for x in p["malware_families"] + p["attack_ids"])
    assert len(p["malware_families"]) <= 10 and len(p["attack_ids"]) <= 10
    assert p["attack_ids"][0] == src["attack_ids"][0]["id"]
    assert p["malware_families"][0] == src["malware_families"][0]["display_name"]
    assert size(out) < 15_000


async def test_cve_general_configurations_and_lists_capped():
    raw = load("cve_general.json")
    server = make_server({CVE_PATH: raw})
    out = await call(server, "get_indicator_details",
                     {"indicator_type": "cve", "indicator_value": "CVE-2021-44228"})
    cfg = out["configurations"]
    assert cfg["node_count"] == 27
    assert cfg["affected_count"] == 201 and cfg["platform_count"] == 23
    assert 0 < len(cfg["affected"]) <= 30 and 0 < len(cfg["platforms"]) <= 10
    assert all(c.startswith("cpe:2.3:") for c in cfg["affected"] + cfg["platforms"])
    assert cfg["note"]
    # Version ranges sharing one wildcard CPE must stay separate and bounded,
    # not collapse into an unbounded "all versions" entry.
    log4j = [c for c in cfg["affected"] if c.startswith("cpe:2.3:a:apache:log4j:*")]
    assert log4j[:3] == [
        "cpe:2.3:a:apache:log4j:*:*:*:*:*:*:*:* (>= 2.0.1, < 2.3.1)",
        "cpe:2.3:a:apache:log4j:*:*:*:*:*:*:*:* (>= 2.4.0, < 2.12.2)",
        "cpe:2.3:a:apache:log4j:*:*:*:*:*:*:*:* (>= 2.13.0, < 2.15.0)",
    ]
    # vulnerable: false entries are platform conditions, never listed as affected.
    assert "cpe:2.3:h:siemens:6bk1602-0aa12-0tp0:-:*:*:*:*:*:*:*" in cfg["platforms"]
    assert not any(c.startswith("cpe:2.3:h:siemens:6bk1602-0aa12-0tp0:-") for c in cfg["affected"])
    assert len(out["exploits"]) <= 21 and out["exploits_total"] == 30
    assert len(out["references"]) <= 21 and out["references_total"] == 30
    assert len(out["pulse_info"]["references"]) <= 20
    assert out["pulse_info"]["count"] == raw["pulse_info"]["count"]
    assert out["cvss"] == raw["cvss"]
    # Version ranges cost ~1.3k chars over a bare CPE list; correctness wins.
    assert size(out) < 28_000


async def test_small_general_response_passes_through():
    server = make_server({
        FILE_PATH: {"indicator": "abc", "pulse_info": {"count": 1, "pulses": [{"name": "p1"}]}}
    })
    out = await call(server, "get_indicator_details",
                     {"indicator_type": "file", "indicator_value": "abc"})
    assert out["pulse_info"]["pulses"] == [{"name": "p1"}]
    assert out["pulse_info"]["count"] == 1


PULSE_TOOLS = [
    ("list_pulse_activity", {"limit": 2}, "/api/v1/pulses/activity"),
    ("list_subscribed_pulses", {}, "/api/v1/pulses/subscribed"),
    ("list_user_pulses", {"username": "alice"}, "/api/v1/pulses/user/alice"),
    ("list_my_pulses", {}, "/api/v1/pulses/my"),
    ("search_pulses", {"query": "x"}, "/api/v1/search/pulses"),
    ("get_related_pulses", {"pulse_id": "abc"}, "/api/v1/pulses/abc/related"),
    ("search_related_pulses", {"adversary": "APT28"}, "/api/v1/pulses/related"),
]


@pytest.mark.parametrize("tool,args,path", PULSE_TOOLS)
async def test_pulse_lists_drop_indicators(tool, args, path):
    raw = load("pulse_activity.json")
    n = len(raw["results"][0]["indicators"])
    server = make_server({path: raw})
    out = await call(server, tool, args)
    for r in out["results"]:
        assert "indicators" not in r
        assert r["indicator_count"] >= 1
        assert "get_pulse_indicators" in r["indicators_note"]
    assert out["results"][0]["indicator_count"] == n
    assert out["count"] == raw["count"]
    assert size(out) < 4_000


async def test_pulse_list_keeps_api_indicator_count():
    raw = {"count": 1, "results": [{"id": "a", "indicator_count": 999,
                                    "indicators": [{"indicator": "1.1.1.1"}]}]}
    server = make_server({"/api/v1/pulses/activity": raw})
    out = await call(server, "list_pulse_activity", {})
    assert out["results"][0]["indicator_count"] == 999


async def test_pulse_details_and_indicators_unchanged():
    ind = {"id": "abc", "name": "n", "indicators": [{"indicator": "1.1.1.1"}]}
    server = make_server({
        "/api/v1/pulses/abc": ind,
        "/api/v1/pulses/abc/indicators": {"count": 1, "results": [{"indicator": "1.1.1.1"}]},
    })
    assert (await call(server, "get_pulse_details", {"pulse_id": "abc"}))["indicators"]
    out = await call(server, "get_pulse_indicators", {"pulse_id": "abc"})
    assert out["results"] == [{"indicator": "1.1.1.1"}]


async def test_search_related_pulses_documents_malware_family_caveat():
    server = make_server({})
    tool = next(t for t in await server.list_tools() if t.name == "search_related_pulses")
    assert "unreliable" in tool.description and "search_pulses" in tool.description
