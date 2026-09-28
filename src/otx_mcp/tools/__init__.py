"""OTX MCP tool registrations.

Each register_* function takes the shared OTXClient and an MCPServer and
registers that domain's tools.
"""

from otx_mcp.api.client import OTXClient
from otx_mcp.tools.indicators import register_indicator_tools
from otx_mcp.tools.pulses import register_pulse_tools
from otx_mcp.tools.search import register_search_tools
from otx_mcp.tools.submissions import register_submission_tools
from otx_mcp.tools.users import register_user_tools

__all__ = [
    "register_indicator_tools",
    "register_pulse_tools",
    "register_search_tools",
    "register_submission_tools",
    "register_user_tools",
]
