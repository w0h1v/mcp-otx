"""Submission tools: URL analysis submission and submission tracking."""

from __future__ import annotations

from typing import Any

from otx_mcp.api.client import OTXClient
from otx_mcp.tools.util import OTXAPIError, ToolError, deep_trim


def register_submission_tools(client: OTXClient, mcp: Any, read_only: bool = False) -> None:
    @mcp.tool()
    async def list_submitted_urls(limit: int = 10, page: int = 1) -> dict[str, Any]:
        """List URLs previously submitted for analysis by your account.

        Args:
            limit: Results per page (1-500).
            page: 1-based page number.

        Returns:
            Paginated submitted-URL status list.
        """
        try:
            data = await client.list_submitted_urls(limit, page)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
        return deep_trim(data)

    @mcp.tool()
    async def list_submitted_files(limit: int = 10, page: int = 1) -> dict[str, Any]:
        """List files previously submitted for analysis by your account.

        Args:
            limit: Results per page (1-500).
            page: 1-based page number.

        Returns:
            Paginated submitted-file status list.
        """
        try:
            data = await client.list_submitted_files(limit, page)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
        return deep_trim(data)

    if read_only:
        return

    @mcp.tool()
    async def submit_url(url: str, tlp: str = "amber") -> dict[str, Any]:
        """Submit a URL to OTX for analysis.

        OTX will visit the URL and analyze returned content. Results appear
        via get_indicator_details with indicator_type "url".

        Args:
            url: The URL to analyze.
            tlp: TLP marking for the submission: white, green, amber or red.

        Returns:
            Submission result from OTX.
        """
        try:
            return await client.submit_url(url, tlp)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e

    @mcp.tool()
    async def submit_urls(urls: list[str], tlp: str = "amber") -> dict[str, Any]:
        """Submit multiple URLs to OTX for bulk analysis.

        Args:
            urls: URLs to analyze.
            tlp: TLP marking for the submissions: white, green, amber or red.

        Returns:
            Bulk submission result from OTX.
        """
        try:
            return await client.submit_urls(urls, tlp)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
