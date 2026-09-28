"""OTX resource registrations."""

from otx_mcp.api.client import OTXClient
from otx_mcp.resources.otx import register_otx_resources

__all__ = ["register_otx_resources"]
