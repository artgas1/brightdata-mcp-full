"""account_management group — 3 hand-written smoke tools (A1 bootstrap).

A2 (INFRA-162) will replace this with auto-generated tools (~44 total) but
will keep the same `register_tools(mcp)` contract.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .bd_account_get_balance import bd_account_get_balance
from .bd_account_get_status import bd_account_get_status
from .bd_zones_list import bd_zones_list

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_tools(mcp: FastMCP) -> None:
    """Register all account_management tools with the FastMCP instance."""
    mcp.tool()(bd_zones_list)
    mcp.tool()(bd_account_get_status)
    mcp.tool()(bd_account_get_balance)


__all__ = [
    "bd_account_get_balance",
    "bd_account_get_status",
    "bd_zones_list",
    "register_tools",
]
