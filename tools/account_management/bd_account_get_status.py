"""bd_account_get_status — get the Bright Data account status.

Hand-written smoke tool for A1 scaffolding. Verified against live API
2026-05-01 — endpoint `GET /status` returns 200.
"""

from __future__ import annotations

from typing import Any

from lib.client import bd_get

GROUP = "account_management"
WRITES = False


async def bd_account_get_status() -> dict[str, Any]:
    """Get the current Bright Data account status.

    Returns the customer account status including:
        - status: e.g. "active"
        - customer: customer ID (e.g. "hl_xxxxxxxx")
        - can_make_requests: bool — whether the account can make billable requests
        - auth_fail_reason: optional reason if auth fails (e.g. "zone_not_found")
        - ip: outbound IP address used for the request

    From: GET /status
    Docs: https://docs.brightdata.com/api-reference/account-management-api/Get_account_status

    Returns:
        On success: dict with the fields above.
        On error: `{"error": str, "status_code": int, "details": ...}`.
    """
    return await bd_get("/status")
