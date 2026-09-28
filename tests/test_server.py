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
    "list_pulse_activity", "get_pulse_events", "create_pulse",
    "subscribe_pulse", "unsubscribe_pulse",
    # indicators
    "get_indicator_details", "validate_indicator", "list_indicator_types",
    "export_indicators",
    # users
    "get_user", "list_user_pulses", "list_my_pulses", "subscribe_user",
    "unsubscribe_user", "follow_user", "unfollow_user",
    # submissions
    "submit_url", "submit_urls", "list_submitted_urls", "list_submitted_files",
}


@pytest.fixture
async def server(client):
    return create_server(client=client)


async def test_all_tools_registered(server):
    tools = {t.name for t in await server.list_tools()}
    assert tools == EXPECTED_TOOLS


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


def test_importable_entry_point():
    from otx_mcp.server import main  # noqa: F401
