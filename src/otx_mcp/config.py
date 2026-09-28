"""Configuration for the OTX MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    api_key: str | None
    api_base: str
    transport: str  # "stdio" | "streamable-http" | "sse"
    host: str
    port: int


def load_config() -> Config:
    return Config(
        api_key=os.getenv("OTX_API_KEY"),
        api_base=os.getenv("OTX_API_BASE", "https://otx.alienvault.com/api/v1"),
        transport=os.getenv("OTX_MCP_TRANSPORT", "stdio"),
        host=os.getenv("OTX_MCP_HOST", "127.0.0.1"),
        port=int(os.getenv("OTX_MCP_PORT", "8000")),
    )
