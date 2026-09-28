"""Async client for the AlienVault OTX / LevelBlue DirectConnect API (v1).

Covers the full public API surface: pulses, indicators (all types and detail
sections), search, users, events, and file/URL submission. Endpoint paths and
per-type section lists were verified against the live API
(https://otx.alienvault.com/api).
"""

from __future__ import annotations

import math
from typing import Any
from urllib.parse import quote

import httpx

# Detail-section whitelist per indicator path type, from each type's `general`
# response `sections` field on the live API.
INDICATOR_SECTIONS: dict[str, tuple[str, ...]] = {
    "IPv4": ("general", "geo", "reputation", "url_list", "passive_dns", "malware", "nids_list", "http_scans"),
    "IPv6": ("general", "geo", "reputation", "url_list", "passive_dns", "malware", "nids_list", "http_scans"),
    "domain": ("general", "geo", "url_list", "passive_dns", "malware", "whois", "http_scans"),
    "hostname": ("general", "geo", "url_list", "passive_dns", "malware", "whois", "http_scans"),
    "file": ("general", "analysis"),
    "url": ("general", "url_list", "http_scans", "screenshot"),
    "cve": ("general", "nids_list", "malware"),
    "nids": ("general",),
    "correlation-rule": ("general",),
}

# Indicator type names accepted by /pulses/indicators/validate and pulse
# creation, from GET /pulses/indicators/types.
INDICATOR_TYPES: tuple[str, ...] = (
    "IPv4", "IPv6", "domain", "hostname", "email", "URL", "URI",
    "FileHash-MD5", "FileHash-SHA1", "FileHash-SHA256", "FileHash-PEHASH",
    "FileHash-IMPHASH", "CIDR", "FilePath", "Mutex", "CVE", "YARA", "JA3",
    "osquery", "SSLCertFingerprint", "BitcoinAddress",
)

DEFAULT_TIMEOUT = httpx.Timeout(60.0, connect=15.0)


class OTXAPIError(Exception):
    """Raised when the OTX API returns an error response."""


class OTXClient:
    """Async client for the OTX DirectConnect API.

    A single shared ``httpx.AsyncClient`` is created lazily and must be closed
    via :meth:`aclose` when the server shuts down.
    """

    def __init__(self, api_key: str | None, api_base: str = "https://otx.alienvault.com/api/v1"):
        if not api_key:
            raise ValueError(
                "OTX API key is required. Set OTX_API_KEY in the environment or .env file."
            )
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None

    @property
    def http(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.api_base,
                headers={"X-OTX-API-KEY": self.api_key, "Accept": "application/json"},
                timeout=DEFAULT_TIMEOUT,
                follow_redirects=True,
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()

    # ------------------------------------------------------------------ core

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_body: Any = None,
        files: dict[str, Any] | None = None,
    ) -> Any:
        response = await self.http.request(
            method, path, params=params, json=json_body, files=files
        )
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text[:300])
            except Exception:
                detail = response.text[:300]
            raise OTXAPIError(f"OTX API {response.status_code} on {method} {path}: {detail}")
        if not response.content:
            return {}
        return response.json()

    async def get(self, path: str, **params: Any) -> Any:
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request("GET", path, params=params or None)

    async def post(self, path: str, body: Any = None, **params: Any) -> Any:
        params = {k: v for k, v in params.items() if v is not None}
        return await self._request("POST", path, params=params or None, json_body=body or {})

    async def patch(self, path: str, body: Any) -> Any:
        return await self._request("PATCH", path, json_body=body)

    @staticmethod
    def _page_params(limit: int = 10, page: int = 1) -> dict[str, int]:
        return {"limit": max(1, min(limit, 500)), "page": max(1, page)}

    # ------------------------------------------------------------- indicators

    async def get_indicator_details(
        self, indicator_type: str, indicator_value: str, section: str = "general"
    ) -> dict[str, Any]:
        """Get one detail section for an indicator.

        ``indicator_type`` is the URL path type (IPv4, IPv6, domain, hostname,
        file, url, cve, nids, correlation-rule); ``indicator_value`` must be a
        single path segment (URLs and IPv6 addresses get URL-encoded).
        """
        sections = INDICATOR_SECTIONS.get(indicator_type)
        if sections is None:
            raise OTXAPIError(
                f"Unknown indicator type {indicator_type!r}. Valid path types: "
                + ", ".join(INDICATOR_SECTIONS)
            )
        if section not in sections:
            raise OTXAPIError(
                f"Section {section!r} not available for {indicator_type}. "
                f"Valid sections: {', '.join(sections)}"
            )
        encoded = quote(indicator_value, safe="")
        return await self.get(f"/indicators/{indicator_type}/{encoded}/{section}")

    async def validate_indicator(
        self, indicator: str, indicator_type: str, description: str = ""
    ) -> dict[str, Any]:
        """Validate an indicator value/type pair (used before adding to pulses)."""
        return await self.get(
            "/pulses/indicators/validate",
            indicator=indicator,
            type=indicator_type,
            description=description or None,
        )

    async def export_indicators(
        self,
        types: list[str] | None = None,
        limit: int = 50,
        page: int = 1,
        modified_since: str | None = None,
    ) -> dict[str, Any]:
        """Bulk export indicators across subscribed pulses (feed sync)."""
        params = self._page_params(limit, page)
        if types:
            params["types"] = ",".join(types)
        if modified_since:
            params["modified_since"] = modified_since
        return await self.get("/indicators/export", **params)

    # ----------------------------------------------------------------- pulses

    async def get_pulse_details(self, pulse_id: str) -> dict[str, Any]:
        """Get full metadata for one pulse (includes its indicators)."""
        return await self.get(f"/pulses/{pulse_id}")

    async def get_pulse_indicators(
        self, pulse_id: str, limit: int = 100, page: int = 1, include_inactive: bool = False
    ) -> dict[str, Any]:
        """Get the (paginated) indicator list of a pulse."""
        return await self.get(
            f"/pulses/{pulse_id}/indicators",
            limit=max(1, min(limit, 1000)),
            page=max(1, page),
            include_inactive=1 if include_inactive else None,
        )

    async def list_subscribed_pulses(
        self, limit: int = 10, page: int = 1, modified_since: str | None = None
    ) -> dict[str, Any]:
        """List pulses from the authenticated user's subscriptions."""
        params = self._page_params(limit, page)
        if modified_since:
            params["modified_since"] = modified_since
        return await self.get("/pulses/subscribed", **params)

    async def list_pulse_activity(
        self,
        types: str | None = None,
        limit: int = 10,
        page: int = 1,
        modified_since: str | None = None,
    ) -> dict[str, Any]:
        """List the latest pulses community-wide (the OTX activity stream)."""
        params = self._page_params(limit, page)
        if types:
            params["types"] = types
        if modified_since:
            params["modified_since"] = modified_since
        return await self.get("/pulses/activity", **params)

    async def get_pulse_events(
        self,
        action: str | None = None,
        limit: int = 10,
        page: int = 1,
        modified_since: str | None = None,
    ) -> dict[str, Any]:
        """List subscription stream events (pulse created/edited/deleted...)."""
        params = self._page_params(limit, page)
        if action:
            params["action"] = action
        if modified_since:
            params["modified_since"] = modified_since
        return await self.get("/pulses/events", **params)

    async def list_indicator_types(self) -> list[dict[str, str]]:
        """List all indicator types usable in pulses (name, slug, description)."""
        data = await self.get("/pulses/indicators/types")
        return data.get("detail", [])

    async def create_pulse(
        self,
        name: str,
        description: str = "",
        public: bool = False,
        tlp: str = "amber",
        tags: list[str] | None = None,
        references: list[str] | None = None,
        indicators: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """Create a pulse. Indicators are dicts with type/indicator/description."""
        if tlp not in ("white", "green", "amber", "red"):
            raise OTXAPIError("tlp must be one of: white, green, amber, red")
        body: dict[str, Any] = {
            "name": name,
            "description": description,
            "public": public,
            "TLP": tlp,
        }
        if tags:
            body["tags"] = tags
        if references:
            body["references"] = references
        if indicators:
            body["indicators"] = indicators
        return await self.post("/pulses/create", body)

    async def edit_pulse(self, pulse_id: str, body: dict[str, Any]) -> dict[str, Any]:
        """Edit a pulse (PATCH semantics: scalar fields replace, lists add/remove)."""
        return await self.patch(f"/pulse/{pulse_id}", body)

    async def delete_pulse(self, pulse_id: str) -> Any:
        """Delete a pulse owned by the authenticated user."""
        return await self.post(f"/pulses/{pulse_id}/delete")

    async def subscribe_pulse(self, pulse_id: str) -> Any:
        return await self.post(f"/pulses/{pulse_id}/subscribe")

    async def unsubscribe_pulse(self, pulse_id: str) -> Any:
        return await self.post(f"/pulses/{pulse_id}/unsubscribe")

    async def clone_pulse(self, pulse_id: str, new_name: str | None = None) -> Any:
        return await self.post(f"/pulses/{pulse_id}/clone", name=new_name)

    # ------------------------------------------------------------------ users

    async def get_user(self, username: str, detailed: bool = True) -> dict[str, Any]:
        """Get a user's profile; detailed=True appends their pulses."""
        return await self.get(f"/users/{username}", detailed=detailed or None)

    async def list_user_pulses(
        self, username: str, limit: int = 10, page: int = 1
    ) -> dict[str, Any]:
        """List pulses authored by a user."""
        return await self.get(f"/pulses/user/{username}", **self._page_params(limit, page))

    async def list_my_pulses(self, limit: int = 10, page: int = 1) -> dict[str, Any]:
        """List pulses authored by the authenticated user."""
        return await self.get("/pulses/my", **self._page_params(limit, page))

    async def subscribe_user(self, username: str) -> Any:
        return await self.post(f"/users/{username}/subscribe")

    async def unsubscribe_user(self, username: str) -> Any:
        return await self.post(f"/users/{username}/unsubscribe")

    async def follow_user(self, username: str) -> Any:
        return await self.post(f"/users/{username}/follow")

    async def unfollow_user(self, username: str) -> Any:
        return await self.post(f"/users/{username}/unfollow")

    # ----------------------------------------------------------------- search

    async def search_pulses(self, query: str, limit: int = 10, page: int = 1) -> dict[str, Any]:
        """Full-text pulse search."""
        return await self.get("/search/pulses", q=query, **self._page_params(limit, page))

    async def search_users(self, query: str, limit: int = 10, page: int = 1) -> dict[str, Any]:
        """Search OTX users by username."""
        return await self.get("/search/users", q=query, **self._page_params(limit, page))

    # ------------------------------------------------------------ submissions

    async def submit_url(self, url: str, tlp: str = "amber") -> Any:
        """Submit a URL for analysis (the URL will be visited by OTX)."""
        if tlp not in ("white", "green", "amber", "red"):
            raise OTXAPIError("tlp must be one of: white, green, amber, red")
        return await self.post("/indicators/submit_url", {"url": url, "tlp": tlp})

    async def submit_urls(self, urls: list[str], tlp: str = "amber") -> Any:
        """Submit multiple URLs for bulk analysis."""
        if tlp not in ("white", "green", "amber", "red"):
            raise OTXAPIError("tlp must be one of: white, green, amber, red")
        return await self.post("/indicators/submit_urls", {"urls": urls, "tlp": tlp})

    async def list_submitted_urls(self, limit: int = 10, page: int = 1) -> dict[str, Any]:
        return await self.get("/indicators/submitted_urls", **self._page_params(limit, page))

    async def submit_file(self, filename: str, content: bytes, tlp: str = "amber") -> Any:
        """Submit a file for static + sandbox analysis."""
        if tlp not in ("white", "green", "amber", "red"):
            raise OTXAPIError("tlp must be one of: white, green, amber, red")
        return await self._request(
            "POST",
            "/indicators/submit_file",
            params={"tlp": tlp},
            files={"file": (filename, content)},
        )

    async def list_submitted_files(self, limit: int = 10, page: int = 1) -> dict[str, Any]:
        return await self.get("/indicators/submitted_files", **self._page_params(limit, page))


def total_pages(result: dict[str, Any], limit: int) -> int:
    """Compute total pages for an OTX paginated response."""
    count = result.get("count") or result.get("full_size") or 0
    return math.ceil(count / limit) if limit else 0
