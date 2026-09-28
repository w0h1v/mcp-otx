"""User tools: profiles, authored pulses, and follow/subscribe actions."""

from __future__ import annotations

from typing import Any

from otx_mcp.api.client import OTXClient
from otx_mcp.tools.util import OTXAPIError, ToolError, deep_trim


def register_user_tools(client: OTXClient, mcp: Any) -> None:
    @mcp.tool()
    async def get_user(username: str, detailed: bool = True) -> dict[str, Any]:
        """Get an OTX user's profile.

        Args:
            username: OTX username.
            detailed: Include the user's recent pulses in the response.

        Returns:
            User profile (subscriber/follower counts, bio, avatar, pulses).
        """
        try:
            return deep_trim(await client.get_user(username, detailed))
        except OTXAPIError as e:
            raise ToolError(str(e)) from e

    @mcp.tool()
    async def list_user_pulses(
        username: str, limit: int = 10, page: int = 1
    ) -> dict[str, Any]:
        """List pulses authored by a specific OTX user.

        Args:
            username: OTX username.
            limit: Results per page (1-500).
            page: 1-based page number.

        Returns:
            Paginated pulse list authored by the user.
        """
        try:
            data = await client.list_user_pulses(username, limit, page)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
        return deep_trim(data)

    @mcp.tool()
    async def list_my_pulses(limit: int = 10, page: int = 1) -> dict[str, Any]:
        """List pulses authored by the authenticated user (your own pulses).

        Args:
            limit: Results per page (1-500).
            page: 1-based page number.

        Returns:
            Paginated list of your pulses.
        """
        try:
            data = await client.list_my_pulses(limit, page)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
        return deep_trim(data)

    @mcp.tool()
    async def subscribe_user(username: str) -> dict[str, Any]:
        """Subscribe to a user; their pulses enter your subscribed feed."""
        try:
            return await client.subscribe_user(username)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e

    @mcp.tool()
    async def unsubscribe_user(username: str) -> dict[str, Any]:
        """Unsubscribe from a user."""
        try:
            return await client.unsubscribe_user(username)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e

    @mcp.tool()
    async def follow_user(username: str) -> dict[str, Any]:
        """Follow a user (their activity shows in your OTX dashboard)."""
        try:
            return await client.follow_user(username)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e

    @mcp.tool()
    async def unfollow_user(username: str) -> dict[str, Any]:
        """Unfollow a user."""
        try:
            return await client.unfollow_user(username)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
