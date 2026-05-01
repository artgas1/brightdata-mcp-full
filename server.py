"""brightdata-mcp-full server entry — FastMCP over stdio.

Loads tool groups based on the `GROUPS` env var (default `account_management`)
and registers each group's tools with the FastMCP instance, then runs stdio.

Usage (in a Claude/MCP client config):

    {
      "mcpServers": {
        "brightdata-full": {
          "command": "uv",
          "args": ["run", "python", "server.py"],
          "env": {
            "BRIGHT_DATA_API_TOKEN": "...",
            "GROUPS": "account_management",
            "BD_ENABLE_WRITES": "false"
          }
        }
      }
    }
"""

from __future__ import annotations

import importlib
import logging
import sys

from fastmcp import FastMCP

from lib.groups import expand_wildcard, load_groups_from_env

logger = logging.getLogger("brightdata-mcp-full")

mcp: FastMCP = FastMCP("brightdata-mcp-full")


def _register_group(group: str) -> int:
    """Import `tools.<group>` and call its register_tools(mcp). Returns tool count.

    Counts tools by introspecting the module's `__all__` / `register_tools` body.
    Each group's __init__.py exposes the tool functions in `__all__` (excluding
    the registration helper itself).
    """
    try:
        module = importlib.import_module(f"tools.{group}")
    except ImportError as e:
        logger.warning("Could not import tools.%s: %s", group, e)
        return 0

    register_fn = getattr(module, "register_tools", None)
    if register_fn is None:
        logger.warning("tools.%s has no register_tools(mcp) — skipping", group)
        return 0

    register_fn(mcp)

    # Count exported tool callables: anything in __all__ that isn't the
    # `register_tools` helper itself.
    exported = getattr(module, "__all__", []) or []
    return sum(1 for name in exported if name != "register_tools")


def main() -> None:
    """Entry point — used by the `brightdata-mcp-full` console script."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )

    groups = expand_wildcard(load_groups_from_env())
    logger.info("Loading groups: %s", groups)

    total = 0
    for group in groups:
        registered = _register_group(group)
        logger.info("  %s: %d tools registered", group, registered)
        total += registered

    logger.info("Total tools registered: %d", total)
    mcp.run()


if __name__ == "__main__":
    main()
