"""Tests for the MCP server surface: tools, resources, and tool execution."""

from __future__ import annotations

import pytest

from otx_mcp.api.client import OTXClient
from otx_mcp.server import create_server

EXPECTED_TOOLS = {
    # search
    "search_pulses", "search_users",
    # pulses
    "get_pulse_details", "get_pulse_indicators", "list_subscribed_pulses",
    "list_pulse_activity", "get_pulse_events", "get_related_pulses",
    "search_related_pulses", "get_subscribed_pulse_ids", "create_pulse",
    "subscribe_pulse", "unsubscribe_pulse",
    # indicators
    "get_indicator_details", "validate_indicator", "list_indicator_types",
    "export_indicators",
    # users
    "get_user", "get_current_user", "list_user_pulses", "list_my_pulses", "subscribe_user",
    "unsubscribe_user", "follow_user", "unfollow_user",
    # submissions
    "submit_url", "submit_urls", "list_submitted_urls", "list_submitted_files",
}


@pytest.fixture
async def server(client):
    return create_server(client=client, read_only=False)


async def test_all_tools_registered(server):
    tools = {t.name for t in await server.list_tools()}
    assert tools == EXPECTED_TOOLS


async def test_read_only_mode_registers_no_write_tools(client):
    from otx_mcp.server import WRITE_TOOL_NAMES, create_server

    ro = create_server(client=client, read_only=True)
    tools = {t.name for t in await ro.list_tools()}
    assert tools == EXPECTED_TOOLS - WRITE_TOOL_NAMES
    assert not (tools & WRITE_TOOL_NAMES)
    assert "READ-ONLY" in ro.description


async def test_read_only_is_the_default(client):
    from otx_mcp.server import WRITE_TOOL_NAMES, create_server

    default = create_server(client=client)  # no explicit read_only
    tools = {t.name for t in await default.list_tools()}
    assert tools == EXPECTED_TOOLS - WRITE_TOOL_NAMES


def test_read_write_flag_parses():
    from otx_mcp.server import parse_args

    assert parse_args([]).read_write is False
    assert parse_args(["--read-write"]).read_write is True


async def test_bearer_middleware_rejects_missing_or_wrong_token():
    from otx_mcp.server import BearerAuthMiddleware

    captured = {}

    async def inner_app(scope, receive, send):
        captured["called"] = True
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def call(headers, scope_type="http"):
        captured.clear()
        msgs = []

        async def send(m):
            msgs.append(m)

        scope = {
            "type": scope_type,
            "headers": [(k.encode(), v.encode()) for k, v in headers.items()],
        }
        await BearerAuthMiddleware(inner_app, "sekrit")(scope, receive, send)
        return msgs

    # no token -> 401, inner app never called
    msgs = await call({})
    assert msgs[0]["status"] == 401
    assert "called" not in captured

    # wrong token -> 401
    msgs = await call({"authorization": "Bearer wrong"})
    assert msgs[0]["status"] == 401
    assert "called" not in captured

    # correct token -> passes through to inner app
    msgs = await call({"authorization": "Bearer sekrit"})
    assert captured.get("called") is True
    assert msgs[0]["status"] == 200

    # non-http scopes (lifespan) forwarded untouched
    forwarded = {}

    async def inner2(scope, receive, send):
        forwarded["scope"] = scope

    async def receive2():
        return {"type": "lifespan.startup"}

    async def send(m):
        pass

    await BearerAuthMiddleware(inner2, "sekrit")(
        {"type": "lifespan"}, receive2, send
    )
    assert forwarded["scope"]["type"] == "lifespan"


async def test_tools_have_descriptions(server):
    for tool in await server.list_tools():
        assert tool.description and tool.description.strip()


async def test_resource_templates_registered(server):
    templates = {t.uri_template for t in await server.list_resource_templates()}
    assert templates == {
        "otx://pulse/{pulse_id}",
        "otx://indicator/{indicator_type}/{indicator_value}",
    }


async def test_call_tool_returns_structured_result(server):
    result = await server.call_tool("get_indicator_details", {
        "indicator_type": "IPv4", "indicator_value": "8.8.8.8",
    })
    assert not result.is_error
    data = result.structured_content
    assert data["indicator"] == "8.8.8.8"
    assert data["pulse_info"]["count"] == 2


async def test_call_tool_invalid_section_raises(server):
    from mcp.server.mcpserver.exceptions import ToolError

    with pytest.raises(ToolError, match="not available for IPv4"):
        await server.call_tool("get_indicator_details", {
            "indicator_type": "IPv4", "indicator_value": "8.8.8.8", "section": "whois",
        })


async def test_read_pulse_resource(server):
    contents = await server.read_resource("otx://pulse/abc123")
    (content,) = list(contents)
    assert '"Test pulse"' in content.content


async def test_read_indicator_resource(server):
    contents = await server.read_resource("otx://indicator/IPv4/8.8.8.8")
    (content,) = list(contents)
    assert '"indicator": "8.8.8.8"' in content.content


async def test_deep_trim_caps_lists(server):
    result = await server.call_tool("get_pulse_indicators", {"pulse_id": "abc123"})
    assert not result.is_error
    trimmed = result.structured_content["results"]
    assert len([r for r in trimmed if isinstance(r, dict)]) <= 50


async def test_call_tool_search_pulses(server):
    result = await server.call_tool(
        "search_pulses", {"query": "test", "limit": 5}
    )
    assert not result.is_error
    assert result.structured_content["results"][0]["id"] == "abc123"


def test_importable_entry_point():
    from otx_mcp.server import main  # noqa: F401
