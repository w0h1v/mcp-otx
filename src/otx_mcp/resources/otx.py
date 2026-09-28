"""OTX resource templates: pulses and indicators addressable by URI."""

from __future__ import annotations

from typing import Any

from otx_mcp.api.client import OTXClient
from otx_mcp.tools.util import OTXAPIError, deep_trim


def register_otx_resources(client: OTXClient, mcp: Any) -> None:
    @mcp.resource(
        "otx://pulse/{pulse_id}",
        name="OTX pulse",
        description="Full metadata for an AlienVault OTX pulse, including its indicators.",
        mime_type="application/json",
    )
    async def get_pulse_resource(pulse_id: str) -> dict[str, Any]:
        return deep_trim(await client.get_pulse_details(pulse_id))

    @mcp.resource(
        "otx://indicator/{indicator_type}/{indicator_value}",
        name="OTX indicator",
        description=(
            "General threat intelligence for an OTX indicator "
            "(types: IPv4, IPv6, domain, hostname, file, url, cve)."
        ),
        mime_type="application/json",
    )
    async def get_indicator_resource(
        indicator_type: str, indicator_value: str
    ) -> dict[str, Any]:
        try:
            return deep_trim(
                await client.get_indicator_details(indicator_type, indicator_value, "general")
            )
        except OTXAPIError as e:
            raise ValueError(str(e)) from e
