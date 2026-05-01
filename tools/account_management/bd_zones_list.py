"""bd_zones_list — list active zones in the Bright Data account.

Hand-written smoke tool for A1 scaffolding. Verified against live API
2026-05-01 — endpoint `GET /zone/get_active_zones` returns 200.
"""

from __future__ import annotations

from typing import Any

from lib.client import bd_get

GROUP = "account_management"
WRITES = False


async def bd_zones_list() -> dict[str, Any]:
    """List the active zones in your Bright Data account.

    Returns each zone's name and type (e.g. `unblocker`, `browser_api`,
    `datacenter`, `residential`, `mobile`, `serp`).

    From: GET /zone/get_active_zones
    Docs: https://docs.brightdata.com/api-reference/account-management-api/Get_active_Zones

    Returns:
        On success: `{"data": [{"name": "...", "type": "..."}, ...], "count": N}`.
        On error: `{"error": str, "status_code": int, "details": ...}`.
    """
    return await bd_get("/zone/get_active_zones")
