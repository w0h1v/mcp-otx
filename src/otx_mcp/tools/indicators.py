"""Indicator tools: full detail-section lookups for every OTX indicator type."""

from __future__ import annotations

from typing import Any

from otx_mcp.api.client import INDICATOR_SECTIONS, INDICATOR_TYPES, OTXClient
from otx_mcp.tools.util import OTXAPIError, ToolError, deep_trim


def register_indicator_tools(client: OTXClient, mcp: Any) -> None:
    @mcp.tool()
    async def get_indicator_details(
        indicator_type: str, indicator_value: str, section: str = "general"
    ) -> dict[str, Any]:
        """Get threat intelligence details for an indicator from AlienVault OTX.

        This is the primary indicator lookup tool. It covers every OTX
        indicator type and detail section in one call.

        Args:
            indicator_type: URL path type. One of: IPv4, IPv6, domain,
                hostname, file (any hash: MD5/SHA1/SHA256/PEHASH/IMPHASH),
                url, cve, nids, correlation-rule.
            indicator_value: The indicator itself (IP address, domain,
                file hash, URL, CVE id...).
            section: Detail section to retrieve. Availability depends on type:
                IPv4/IPv6: general, geo, reputation, url_list, passive_dns,
                malware, nids_list, http_scans | domain/hostname: general, geo,
                url_list, passive_dns, malware, whois, http_scans |
                file: general, analysis (sandbox report) | url: general,
                url_list, http_scans, screenshot | cve: general, nids_list,
                malware. Use 'general' first: it includes pulse associations,
                reputation and geo summaries.

        Returns:
            The raw JSON for the requested section (lists capped at 50 items
            with counts preserved).
        """
        try:
            data = await client.get_indicator_details(indicator_type, indicator_value, section)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
        return deep_trim(data)

    @mcp.tool()
    async def validate_indicator(
        indicator: str, indicator_type: str, description: str = ""
    ) -> dict[str, Any]:
        """Validate an indicator value/type pair before using it in a pulse.

        Args:
            indicator: The indicator value to validate.
            indicator_type: OTX indicator type name, e.g. IPv4, domain,
                FileHash-SHA256, URL, CVE, YARA, JA3, Mutex, CIDR, email.
            description: Optional description used during validation.

        Returns:
            Validation result from OTX (includes access_type and expiration).
        """
        try:
            return await client.validate_indicator(indicator, indicator_type, description)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e

    @mcp.tool()
    async def list_indicator_types() -> list[dict[str, str]]:
        """List every indicator type usable in OTX pulses, with descriptions.

        Use this to discover valid indicator_type values for
        validate_indicator and create_pulse.
        """
        try:
            return await client.list_indicator_types()
        except OTXAPIError as e:
            raise ToolError(str(e)) from e

    @mcp.tool()
    async def export_indicators(
        types: list[str] | None = None,
        limit: int = 50,
        page: int = 1,
        modified_since: str | None = None,
    ) -> dict[str, Any]:
        """Bulk export indicators across all subscribed pulses (feed sync).

        Args:
            types: Indicator type names to include (e.g. ["domain", "IPv4",
                "FileHash-SHA256"]); omit for all types.
            limit: Results per page (1-500).
            page: 1-based page number.
            modified_since: ISO 8601 timestamp; only return indicators from
                pulses modified after this time.

        Returns:
            Paginated indicator export from OTX.
        """
        try:
            data = await client.export_indicators(types, limit, page, modified_since)
        except OTXAPIError as e:
            raise ToolError(str(e)) from e
        return deep_trim(data)

    # Surface the canonical type lists in tool metadata consumers can import.
    get_indicator_details.__otx_path_types__ = tuple(INDICATOR_SECTIONS)
    validate_indicator.__otx_type_names__ = INDICATOR_TYPES
