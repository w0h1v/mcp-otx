"""Search tools for pulses and users."""

from __future__ import annotations

from typing import Any

from otx_mcp.api.client import OTXClient
from otx_mcp.tools.util import OTXAPIError, ToolError, deep_trim


def register_search_tools(client: OTXClient, mcp: Any) -> None:
    @mcp.tool()
    async def search_pulses(query: str, limit: int = 10, page: int = 1) -> dict[str, Any]:
        """Full-text search across all public OTX pulses.

        The best starting point for threat research: search for a malware
        family, actor, campaign or technology and get matching pulses with
        their IDs, then pull details or indicators.

        Args:
            query: Search terms.
            limit: Results per page (1-500).
            page: 1-based page number.

        Returns:
            Paginated matching pulses.
        """
        try:
            data = await client.search_pulses(query, limit, page)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
        return deep_trim(data)

    @mcp.tool()
    async def search_users(query: str, limit: int = 10, page: int = 1) -> dict[str, Any]:
        """Search OTX users by username.

        Args:
            query: Username (or fragment) to search for.
            limit: Results per page (1-500).
            page: 1-based page number.

        Returns:
            Paginated matching users.
        """
        try:
            data = await client.search_users(query, limit, page)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
        return deep_trim(data)
