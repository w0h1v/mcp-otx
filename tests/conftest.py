"""Shared fixtures: an OTXClient backed by a mock transport."""

from __future__ import annotations

import json

import httpx
import pytest

from otx_mcp.api.client import OTXClient


def handler(request: httpx.Request) -> httpx.Response:
    """Minimal fake of the OTX API covering the routes the client uses."""
    path = request.url.path
    params = request.url.params

    if path == "/api/v1/search/pulses":
        return httpx.Response(200, json={
            "count": 1,
            "next": None,
            "results": [{"id": "abc123", "name": "Test pulse", "author_name": "alice"}],
        })
    if path == "/api/v1/search/users":
        return httpx.Response(200, json={
            "results": [{"username": "alice", "subscriber_count": 5}]
        })
    if path == "/api/v1/pulses/abc123":
        return httpx.Response(200, json={
            "id": "abc123", "name": "Test pulse",
            "indicators": [{"type": "IPv4", "indicator": "8.8.8.8"}],
        })
    if path == "/api/v1/pulses/abc123/indicators":
        return httpx.Response(200, json={
            "count": 1, "results": [{"type": "IPv4", "indicator": "8.8.8.8"}],
        })
    if path == "/api/v1/pulses/subscribed":
        assert params.get("limit") == "10" and params.get("page") == "2"
        if params.get("modified_since"):
            assert "T" in params["modified_since"]
        return httpx.Response(200, json={"count": 0, "results": []})
    if path == "/api/v1/pulses/activity":
        return httpx.Response(200, json={"count": 0, "results": []})
    if path == "/api/v1/pulses/events":
        return httpx.Response(200, json={"count": 0, "results": []})
    if path == "/api/v1/pulses/indicators/types":
        return httpx.Response(200, json={
            "detail": [{"name": "IPv4", "slug": "ip", "description": "An IPv4 address"}]
        })
    if path == "/api/v1/pulses/indicators/validate":
        assert params.get("indicator") == "8.8.8.8"
        return httpx.Response(200, json={"access_type": "public"})
    if path == "/api/v1/pulses/create":
        body = json.loads(request.content)
        return httpx.Response(200, json={"id": "newpulse", "name": body["name"]})
    if path == "/api/v1/indicators/IPv4/8.8.8.8/general":
        return httpx.Response(200, json={
            "indicator": "8.8.8.8", "type": "IPv4",
            "pulse_info": {"count": 2, "pulses": [{"name": "p1"}, {"name": "p2"}]},
        })
    if path == "/api/v1/indicators/IPv4/8.8.8.8/reputation":
        return httpx.Response(200, json={"reputation": {"threat_score": 0}})
    if path == "/api/v1/indicators/file/deadbeef/analysis":
        return httpx.Response(200, json={"analysis": {"plugins": {}}})
    if path == "/api/v1/users/alice":
        assert params.get("detailed") == "true"
        return httpx.Response(200, json={"username": "alice", "subscriber_count": 5})
    if path == "/api/v1/pulses/user/alice":
        return httpx.Response(200, json={"count": 0, "results": []})
    if path == "/api/v1/pulses/my":
        return httpx.Response(200, json={"count": 0, "results": []})
    if path == "/api/v1/users/alice/subscribe":
        return httpx.Response(200, json={"subscribed": True})
    if path == "/api/v1/pulses/abc123/subscribe":
        return httpx.Response(200, json={"subscribed": True})
    if path == "/api/v1/indicators/submit_url":
        return httpx.Response(200, json={"url": json.loads(request.content)["url"]})
    if path == "/api/v1/indicators/export":
        return httpx.Response(200, json={"count": 0, "results": []})
    if path == "/api/v1/indicators/IPv4/1.2.3.4/general":
        return httpx.Response(404, json={"detail": "not found"})
    return httpx.Response(404, json={"detail": f"endpoint not found: {path}"})


@pytest.fixture
async def client():
    c = OTXClient("test-key", "https://otx.test/api/v1")
    transport = httpx.MockTransport(handler)
    c._client = httpx.AsyncClient(
        base_url=c.api_base,
        headers={"X-OTX-API-KEY": c.api_key, "Accept": "application/json"},
        timeout=httpx.Timeout(60.0, connect=15.0),
        transport=transport,
    )
    try:
        yield c
    finally:
        await c.aclose()
