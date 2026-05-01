"""Safety gates for write operations.

All write tools (POST/PUT/DELETE) are wrapped with `requires_write_enabled`.
Without `BD_ENABLE_WRITES=true` in env, calls return a structured error
instead of executing — protects against accidental zone create/delete/etc.
"""

from __future__ import annotations

import functools
import os
from collections.abc import Awaitable, Callable
from typing import Any

WRITE_DISABLED_ERROR = {
    "error": "Write operations disabled. Set BD_ENABLE_WRITES=true to enable.",
    "hint": (
        "This tool performs a write (POST/PUT/DELETE) against your Bright Data "
        "account. To enable it, set the environment variable BD_ENABLE_WRITES=true "
        "in your MCP client config and restart the server."
    ),
    "status_code": 0,
}


def writes_enabled() -> bool:
    """Return True if BD_ENABLE_WRITES env var is set to 'true' (case-insensitive)."""
    return os.environ.get("BD_ENABLE_WRITES", "").strip().lower() == "true"


def requires_write_enabled[**P](
    func: Callable[P, Awaitable[dict[str, Any]]],
) -> Callable[P, Awaitable[dict[str, Any]]]:
    """Decorator gating a write tool. Returns structured error if writes disabled.

    Usage:
        @requires_write_enabled
        async def bd_zone_create(name: str) -> dict:
            return await bd_post("/zone", json={"zone": {"name": name}})

    The wrapped function still has its original signature for type-checking and
    introspection (used by FastMCP to build the tool schema).
    """

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> dict[str, Any]:
        if not writes_enabled():
            return dict(WRITE_DISABLED_ERROR)
        return await func(*args, **kwargs)

    return wrapper
