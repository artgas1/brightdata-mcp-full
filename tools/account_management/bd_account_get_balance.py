"""bd_account_get_balance — get the total Bright Data account balance.

Hand-written smoke tool for A1 scaffolding. Endpoint per official BD OpenAPI spec.

# SMOKE-TOOL: hand-written, do not regenerate

NOTE on permissions: this endpoint requires the API token to have the
"customer balance" permission. With the default test token used during A1
verification (2026-05-01), `GET /customer/balance` returns HTTP 403 with
message "Your API key lacks the required permissions for this action.
You can change your token permissions at https://brightdata.com/cp/setting/users".

The endpoint path itself is correct per BD's published OpenAPI spec at
https://docs.brightdata.com/api-reference/account-management-api/Get_total_balance_through_API
— the 403 reflects the test token's scope, not a wrong path. Tools return
structured errors (not exceptions) so 403s surface to the MCP client cleanly.
"""

from __future__ import annotations

from typing import Any

from lib.client import bd_get

GROUP = "account_management"
WRITES = False


async def bd_account_get_balance() -> dict[str, Any]:
    """Get the total balance through the Bright Data API.

    Returns the current account balance and pending balance (the amount that
    will be billed in the next billing cycle).

    Requires the API token to have "customer balance" permission. Tokens
    without this permission receive a structured 403 error.

    From: GET /customer/balance
    Docs: https://docs.brightdata.com/api-reference/account-management-api/Get_total_balance_through_API

    Returns:
        On success: `{"balance": <number>, "pending_balance": <number>}`.
        On error: `{"error": str, "status_code": int, "details": ...}`.
    """
    return await bd_get("/customer/balance")
