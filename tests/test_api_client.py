"""Tests for the OTX API client against a mocked OTX backend."""

from __future__ import annotations

import pytest
from otx_mcp.api.client import INDICATOR_SECTIONS, OTXAPIError, OTXClient, total_pages


async def test_requires_api_key():
    with pytest.raises(ValueError, match="OTX_API_KEY"):
        OTXClient(None)


async def test_search_pulses(client):
    data = await client.search_pulses("test query", limit=5)
    assert data["count"] == 1
    assert data["results"][0]["id"] == "abc123"


async def test_pagination_params_sent(client):
    data = await client.list_subscribed_pulses(limit=10, page=2, modified_since="2026-01-01T00:00:00")
    assert data == {"count": 0, "results": []}


async def test_get_pulse_details(client):
    pulse = await client.get_pulse_details("abc123")
    assert pulse["name"] == "Test pulse"
    assert pulse["indicators"][0]["indicator"] == "8.8.8.8"

async def test_indicator_url_encoding(client):
    # The mock route only matches when the value was percent-encoded into a
    # single path segment (its decoded path contains "?q=1"); an unencoded
    # value splinters into path+query and misses the route (404).
    data = await client.get_indicator_details(
        "url", "https://example.com/a path?q=1", "general"
    )
    assert data["indicator"] == "https://example.com/a path?q=1"


async def test_pulse_id_query_injection_is_encoded(client):
    # A '?' in pulse_id must be encoded into the segment; the mock's GET-pulse
    # route asserts no stray query params arrive, and an unencoded value would
    # turn this request into /pulses/subscribed?x=1 (the subscribed feed).
    with pytest.raises(OTXAPIError, match="404"):
        await client.get_pulse_details("subscribed?x=1")


async def test_indicator_general(client):
    data = await client.get_indicator_details("IPv4", "8.8.8.8")
    assert data["indicator"] == "8.8.8.8"
    assert data["pulse_info"]["count"] == 2


async def test_indicator_specific_section(client):
    data = await client.get_indicator_details("IPv4", "8.8.8.8", "reputation")
    assert data["reputation"]["threat_score"] == 0




async def test_indicator_unknown_type_rejected(client):
    with pytest.raises(OTXAPIError, match="Unknown indicator type"):
        await client.get_indicator_details("banana", "8.8.8.8")


async def test_indicator_invalid_section_rejected(client):
    with pytest.raises(OTXAPIError, match="not available for IPv4"):
        await client.get_indicator_details("IPv4", "8.8.8.8", "whois")


async def test_api_error_surfaces_status(client):
    with pytest.raises(OTXAPIError, match="404"):
        await client.get_indicator_details("IPv4", "1.2.3.4")


async def test_user_endpoints(client):
    user = await client.get_user("alice")
    assert user["username"] == "alice"
    assert (await client.list_user_pulses("alice"))["count"] == 0
    assert (await client.list_my_pulses())["count"] == 0
    assert (await client.subscribe_user("alice")) == {"subscribed": True}


async def test_validate_indicator_posts_body(client):
    data = await client.validate_indicator("8.8.8.8", "IPv4")
    assert data["access_type"] == "public"
    assert data["status"] == "success"


async def test_indicator_types(client):
    types = await client.list_indicator_types()
    assert types[0]["name"] == "IPv4"


async def test_create_pulse_validates_tlp(client):
    with pytest.raises(OTXAPIError, match="tlp"):
        await client.create_pulse("name", tlp="orange")


async def test_create_pulse(client):
    pulse = await client.create_pulse(
        "New threat",
        description="desc",
        tlp="green",
        tags=["malware"],
        indicators=[{"type": "IPv4", "indicator": "8.8.8.8"}],
    )
    assert pulse["id"] == "newpulse"


async def test_submit_url(client):
    result = await client.submit_url("https://example.com/")
    assert result["url"] == "https://example.com/"


async def test_submit_url_validates_tlp(client):
    with pytest.raises(OTXAPIError, match="tlp"):
        await client.submit_url("https://example.com/", tlp="purple")


def test_section_whitelist_matches_types():
    assert "passive_dns" in INDICATOR_SECTIONS["domain"]
    assert "analysis" in INDICATOR_SECTIONS["file"]
    assert "whois" in INDICATOR_SECTIONS["hostname"]
    assert "whois" not in INDICATOR_SECTIONS["IPv4"]
    assert set(INDICATOR_SECTIONS["url"]) >= {"url_list", "http_scans"}


def test_total_pages():
    assert total_pages({"count": 25}, 10) == 3
    assert total_pages({"count": 0}, 10) == 0
    assert total_pages({"full_size": 10}, 10) == 1


async def test_edit_pulse_patches_plural_route(client):
    data = await client.edit_pulse("abc123", {"name": "renamed"})
    assert data == {"id": "abc123", "patched": True}


async def test_clone_pulse_sends_name_in_body(client):
    data = await client.clone_pulse("abc123", "renamed")
    assert data == {"id": "clone123", "name": "renamed"}


async def test_timeout_becomes_otx_api_error():
    import httpx

    from otx_mcp.api.client import OTXClient

    c = OTXClient("k", "https://otx.test/api/v1")

    async def hang(request):
        raise httpx.ConnectTimeout("too slow")

    c._client = httpx.AsyncClient(transport=httpx.MockTransport(hang))
    try:
        with pytest.raises(OTXAPIError, match="timed out"):
            await c.get_pulse_details("abc123")
    finally:
        await c.aclose()


async def test_network_error_becomes_otx_api_error():
    import httpx

    from otx_mcp.api.client import OTXClient

    c = OTXClient("k", "https://otx.test/api/v1")

    async def boom(request):
        raise httpx.ConnectError("no route to host")

    c._client = httpx.AsyncClient(transport=httpx.MockTransport(boom))
    try:
        with pytest.raises(OTXAPIError, match="OTX request failed"):
            await c.search_pulses("x")
    finally:
        await c.aclose()


def test_deep_trim_truncates_strings():
    from otx_mcp.tools.util import deep_trim

    long_text = "A" * 9000
    out = deep_trim({"whois": long_text})
    assert out["whois"].startswith("A" * 4000)
    assert "[truncated, 9000 chars total]" in out["whois"]
    assert deep_trim("short") == "short"


async def test_get_current_user(client):
    me = await client.get_current_user()
    assert me["username"] == "self"


async def test_subscribed_pulse_ids(client):
    data = await client.get_subscribed_pulse_ids()
    assert data["count"] == 42
    assert data["results"] == ["546ce8eb11d40838dc6e43f1"]


async def test_get_related_pulses(client):
    data = await client.get_related_pulses("abc123")
    assert data["results"][0]["name"] == "Related"


async def test_search_related_pulses_requires_exactly_one_selector(client):
    with pytest.raises(OTXAPIError, match="Exactly one"):
        await client.search_related_pulses()
    with pytest.raises(OTXAPIError, match="Exactly one"):
        await client.search_related_pulses(pulse_id="abc", adversary="APT1")
    data = await client.search_related_pulses(malware_family="trickbot")
    assert data["results"][0]["matched_on"] == "malware_family"


async def test_update_submitted_urls_tlp(client):
    assert await client.update_submitted_urls_tlp(["https://x.example/"], "green") == {"updated": 1}
    with pytest.raises(OTXAPIError, match="tlp"):
        await client.update_submitted_urls_tlp(["https://x.example/"], "orange")
