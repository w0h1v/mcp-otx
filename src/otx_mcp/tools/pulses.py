"""Pulse tools: retrieval, feeds, events, and pulse lifecycle actions."""

from __future__ import annotations

from typing import Any

from otx_mcp.api.client import OTXClient
from otx_mcp.tools.util import OTXAPIError, ToolError, deep_trim


def register_pulse_tools(client: OTXClient, mcp: Any, read_only: bool = False) -> None:
    @mcp.tool()
    async def get_pulse_details(pulse_id: str) -> dict[str, Any]:
        """Get full details of an OTX pulse by ID.

        Includes name, author, description, TLP, tags, references, threat
        categories (Adversary, Malware, TTPs) and the pulse's indicators.

        Args:
            pulse_id: 24-character hex pulse ID (from search results,
                activity feeds, or OTX URLs).

        Returns:
            Pulse metadata with its indicator list (capped at 50 shown).
        """
        try:
            return deep_trim(await client.get_pulse_details(pulse_id))
        except OTXAPIError as e:
            raise ToolError(str(e)) from e

    @mcp.tool()
    async def get_pulse_indicators(
        pulse_id: str, limit: int = 100, page: int = 1, include_inactive: bool = False
    ) -> dict[str, Any]:
        """List the indicators contained in a pulse (paginated).

        Args:
            pulse_id: 24-character hex pulse ID.
            limit: Results per page (1-1000).
            page: 1-based page number.
            include_inactive: Include indicators the pulse author deactivated.

        Returns:
            Paginated indicator list for the pulse.
        """
        try:
            data = await client.get_pulse_indicators(pulse_id, limit, page, include_inactive)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
        return deep_trim(data)

    @mcp.tool()
    async def list_subscribed_pulses(
        limit: int = 10, page: int = 1, modified_since: str | None = None
    ) -> dict[str, Any]:
        """List pulses from your OTX subscriptions.

        Includes pulses you subscribed to, pulses from users and groups you
        follow, and pulses you created.

        Args:
            limit: Results per page (1-500).
            page: 1-based page number.
            modified_since: ISO 8601 timestamp; only pulses created or
                modified after this time.

        Returns:
            Paginated list of subscribed pulses.
        """
        try:
            data = await client.list_subscribed_pulses(limit, page, modified_since)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
        return deep_trim(data)

    @mcp.tool()
    async def list_pulse_activity(
        limit: int = 10, page: int = 1, modified_since: str | None = None
    ) -> dict[str, Any]:
        """List the latest pulses across the whole OTX community.

        Args:
            limit: Results per page (1-500).
            page: 1-based page number.
            modified_since: ISO 8601 timestamp cutoff.

        Returns:
            Paginated activity-stream pulses.
        """
        try:
            data = await client.list_pulse_activity(limit, page, modified_since)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
        return deep_trim(data)

    @mcp.tool()
    async def get_pulse_events(
        limit: int = 10, page: int = 1, modified_since: str | None = None
    ) -> dict[str, Any]:
        """List events from your subscription stream (pulse lifecycle changes).

        Useful for incremental sync: each event carries an `action` field
        (e.g. remove_pulse) naming what happened to which pulse.

        Args:
            limit: Results per page (1-500).
            page: 1-based page number.
            modified_since: ISO 8601 timestamp cutoff.

        Returns:
            Paginated subscription-stream events.
        """
        try:
            data = await client.get_pulse_events(limit, page, modified_since)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
        return deep_trim(data)

    @mcp.tool()
    async def get_related_pulses(
        pulse_id: str, limit: int = 10, page: int = 1
    ) -> dict[str, Any]:
        """Get pulses that share indicators (IOCs) with the given pulse.

        Args:
            pulse_id: 24-character hex pulse ID.
            limit: Results per page (1-500).
            page: 1-based page number.

        Returns:
            Paginated related pulses.
        """
        try:
            data = await client.get_related_pulses(pulse_id, limit, page)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
        return deep_trim(data)

    @mcp.tool()
    async def search_related_pulses(
        pulse_id: str | None = None,
        malware_family: str | None = None,
        adversary: str | None = None,
        limit: int = 10,
        page: int = 1,
    ) -> dict[str, Any]:
        """Find pulses related to a pulse, malware family, or adversary.

        Pass exactly ONE of pulse_id, malware_family or adversary. For a
        pulse, returns other pulses sharing some of the same IOCs; for a
        malware family or adversary, returns pulses tagged with it.

        Args:
            pulse_id: Pulse to find related pulses for.
            malware_family: Malware family name (e.g. "trickbot").
            adversary: Adversary name (e.g. "Equation Group").
            limit: Results per page (1-500).
            page: 1-based page number.

        Returns:
            Paginated related pulses.
        """
        try:
            data = await client.search_related_pulses(
                pulse_id, malware_family, adversary, limit, page
            )
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
        return deep_trim(data)

    @mcp.tool()
    async def get_subscribed_pulse_ids(
        limit: int = 500, page: int = 1
    ) -> dict[str, Any]:
        """Get just the IDs of your subscribed pulses (lightweight sync).

        Args:
            limit: Results per page (1-500).
            page: 1-based page number.

        Returns:
            Paginated pulse-ID list.
        """
        try:
            data = await client.get_subscribed_pulse_ids(limit, page)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
        return deep_trim(data)

    if read_only:
        return

    @mcp.tool()
    async def create_pulse(
        name: str,
        description: str = "",
        public: bool = False,
        tlp: str = "amber",
        tags: list[str] | None = None,
        references: list[str] | None = None,
        indicators: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """Create a new OTX pulse owned by the authenticated user.

        Validate indicators with validate_indicator first. Each indicator is
        {"type": <indicator type name>, "indicator": <value>, "description":
        "..."}.

        Args:
            name: Pulse title.
            description: Markdown description of the threat.
            public: Whether the pulse is publicly visible.
            tlp: TLP marking: white, green, amber or red.
            tags: Threat tags (e.g. ["malware", "rat"]).
            references: Reference URLs.
            indicators: Indicators to include; see validate_indicator.

        Returns:
            The created pulse (with its new ID).
        """
        try:
            return await client.create_pulse(
                name, description, public, tlp, tags, references, indicators
            )
        except OTXAPIError as e:
            raise ToolError(str(e)) from e

    @mcp.tool()
    async def subscribe_pulse(pulse_id: str) -> dict[str, Any]:
        """Subscribe to a pulse so its indicators enter your feeds."""
        try:
            return await client.subscribe_pulse(pulse_id)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e

    @mcp.tool()
    async def unsubscribe_pulse(pulse_id: str) -> dict[str, Any]:
        """Unsubscribe from a pulse."""
        try:
            return await client.unsubscribe_pulse(pulse_id)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
