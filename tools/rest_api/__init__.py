"""rest_api group — no tools (spec not mapped or empty)."""
# ruff: noqa
# pyright: ignore

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_tools(mcp: FastMCP) -> None:
    """No-op — this group has no tools yet."""
    _ = mcp
    return None


__all__ = ["register_tools"]
