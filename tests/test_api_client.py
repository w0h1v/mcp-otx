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
    # URLs must be percent-encoded into a single path segment; the mock has no
    # route for this indicator, so a 404 OTXAPIError proves the request was
    # sent as one encoded segment rather than splintering the path.
    with pytest.raises(OTXAPIError, match="404"):
        await client.get_indicator_details(
            "url", "https://example.com/a path?q=1", "general"
        )


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


async def test_validate_indicator(client):
    data = await client.validate_indicator("8.8.8.8", "IPv4")
    assert data["access_type"] == "public"


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
