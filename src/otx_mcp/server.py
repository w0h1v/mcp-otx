"""OTX MCP server: tool/resource registration and transport entry point."""

from __future__ import annotations

import argparse
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.mcpserver import MCPServer

from otx_mcp import __version__
from otx_mcp.api.client import OTXClient
from otx_mcp.config import load_config
from otx_mcp.resources import register_otx_resources
from otx_mcp.tools import (
    register_indicator_tools,
    register_pulse_tools,
    register_search_tools,
    register_submission_tools,
    register_user_tools,
)

INSTRUCTIONS = """AlienVault OTX (Open Threat Exchange) threat intelligence server.

Workflow guidance:
- Explore threats: search_pulses, then get_pulse_details / get_pulse_indicators.
- Enrich an observable: get_indicator_details (supports IPv4/IPv6/domain/
  hostname/file hash/URL/CVE; start with section "general", then pull
  reputation, geo, passive_dns, malware, url_list, whois or analysis as needed).
- Track sources: get_user / list_user_pulses, subscribe_user, follow_user.
- Feeds: list_subscribed_pulses, list_pulse_activity, get_pulse_events,
  export_indicators.
- Publish: validate_indicator then create_pulse.
"""


def create_server(client: OTXClient | None = None) -> MCPServer:
    """Create the MCPServer with all OTX tools and resources registered.

    Args:
        client: Pre-built OTXClient (e.g. a test double). A real one is
            created from the environment when omitted.
    """
    if client is None:
        config = load_config()
        client = OTXClient(config.api_key, config.api_base)

    @asynccontextmanager
    async def lifespan(server: MCPServer) -> AsyncIterator[OTXClient]:
        try:
            yield client
        finally:
            await client.aclose()

    mcp = MCPServer(
        "otx-server",
        title="AlienVault OTX MCP Server",
        description=(
            "Threat intelligence from AlienVault OTX / LevelBlue Open Threat "
            "Exchange: pulses, indicators, reputation, passive DNS, malware "
            "analysis, and more."
        ),
        instructions=INSTRUCTIONS,
        version=__version__,
        lifespan=lifespan,
    )

    register_search_tools(client, mcp)
    register_pulse_tools(client, mcp)
    register_indicator_tools(client, mcp)
    register_user_tools(client, mcp)
    register_submission_tools(client, mcp)
    register_otx_resources(client, mcp)
    return mcp


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    config = load_config()
    parser = argparse.ArgumentParser(
        prog="otx-mcp",
        description="AlienVault OTX MCP server (stdio and streamable HTTP transports)",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http", "sse"],
        default=config.transport,
        help=f"MCP transport to serve (default: {config.transport} from OTX_MCP_TRANSPORT)",
    )
    parser.add_argument(
        "--host",
        default=config.host,
        help=f"HTTP bind host (default: {config.host} from OTX_MCP_HOST)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=config.port,
        help=f"HTTP bind port (default: {config.port} from OTX_MCP_PORT)",
    )
    parser.add_argument(
        "--json-response",
        action="store_true",
        help="Respond with plain JSON instead of SSE streams (streamable-http only)",
    )
    parser.add_argument(
        "--stateless-http",
        action="store_true",
        help="Run streamable-http in stateless mode (one session per request)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    config = load_config()
    if not config.api_key:
        print(
            "error: OTX_API_KEY is not set. Export it or put it in a .env file.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    server = create_server()
    if args.transport == "stdio":
        server.run(transport="stdio")
    elif args.transport == "sse":
        server.run(transport="sse", host=args.host, port=args.port)
    else:
        server.run(
            transport="streamable-http",
            host=args.host,
            port=args.port,
            json_response=args.json_response,
            stateless_http=args.stateless_http,
        )


if __name__ == "__main__":
    main()
