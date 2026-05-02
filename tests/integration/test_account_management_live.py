"""Live integration tests for account_management read-only tools.

These hit the real Bright Data API using `BRIGHT_DATA_API_TOKEN`. The token
provided for A3 testing has zone-management access but NOT the
"customer balance" permission, so `bd_account_get_balance` is expected to
return a structured 403 — that's a test assertion, not a failure.

Naming
------
Each test asserts on the structured response shape returned by `bd_request`:
- success → dict with no `error` key (and possibly `data`/`count` for lists)
- error → `{"error": str, "status_code": int, "details": ...}` (never raises)
"""

from __future__ import annotations

import pytest

from tools.account_management.bd_account_get_balance import bd_account_get_balance
from tools.account_management.bd_account_get_status import bd_account_get_status
from tools.account_management.bd_account_management_get_zone import (
    bd_account_management_get_zone,
)
from tools.account_management.bd_account_management_get_zone_blacklist import (
    bd_account_management_get_zone_blacklist,
)
from tools.account_management.bd_account_management_get_zone_whitelist import (
    bd_account_management_get_zone_whitelist,
)
from tools.account_management.bd_account_management_list_zone_get_active_zones import (
    bd_account_management_list_zone_get_active_zones,
)
from tools.account_management.bd_account_management_list_zone_get_all_zones import (
    bd_account_management_list_zone_get_all_zones,
)
from tools.account_management.bd_account_management_list_zone_passwords import (
    bd_account_management_list_zone_passwords,
)
from tools.account_management.bd_account_management_list_zone_permissions import (
    bd_account_management_list_zone_permissions,
)
from tools.account_management.bd_zones_list import bd_zones_list

from .conftest import KNOWN_ZONE

pytestmark = pytest.mark.asyncio


def _is_error(resp: dict) -> bool:
    return "error" in resp


# --------------------------------------------------------------------------- #
# Hand-written smoke tools (A1)                                               #
# --------------------------------------------------------------------------- #


async def test_bd_account_get_status_returns_account_metadata(bd_token: str) -> None:
    """`GET /status` returns customer ID, status, IP for the test account."""
    _ = bd_token
    resp = await bd_account_get_status()
    assert not _is_error(resp), f"unexpected error: {resp}"
    assert resp.get("status") == "active"
    assert resp.get("customer", "").startswith("hl_")
    # `can_make_requests` may be False if the account has no billable plan.
    assert "can_make_requests" in resp
    assert "ip" in resp


async def test_bd_zones_list_returns_active_zones(bd_token: str) -> None:
    """A1 smoke tool — the test account has at least one active zone."""
    _ = bd_token
    resp = await bd_zones_list()
    assert not _is_error(resp), f"unexpected error: {resp}"
    # bd_request wraps top-level lists into {"data": [...], "count": N}
    assert "data" in resp
    assert resp["count"] >= 1
    assert all("name" in z and "type" in z for z in resp["data"])


async def test_bd_account_get_balance_returns_403_with_test_token(bd_token: str) -> None:
    """The A3 test token lacks `customer balance` permission — expect a 403.

    This is documented in the smoke tool's docstring. Verifying the structured
    error shape ensures the client doesn't raise on 4xx and the MCP layer can
    surface it cleanly.
    """
    _ = bd_token
    resp = await bd_account_get_balance()
    assert _is_error(resp), f"expected 403 error, got {resp}"
    assert resp["status_code"] == 403
    assert "permission" in str(resp.get("details", "")).lower() or "permission" in resp["error"].lower()


# --------------------------------------------------------------------------- #
# Auto-generated read-only zone tools                                         #
# --------------------------------------------------------------------------- #


async def test_list_active_zones_via_codegen(bd_token: str) -> None:
    """Auto-generated GET /zone/get_active_zones — should match A1 smoke tool."""
    _ = bd_token
    resp = await bd_account_management_list_zone_get_active_zones()
    assert not _is_error(resp), f"unexpected error: {resp}"
    assert "data" in resp
    assert resp["count"] >= 1


async def test_list_all_zones_includes_known_zone(bd_token: str) -> None:
    """`GET /zone/get_all_zones` — superset of active zones, includes status field."""
    _ = bd_token
    resp = await bd_account_management_list_zone_get_all_zones()
    assert not _is_error(resp), f"unexpected error: {resp}"
    zones = resp["data"]
    names = {z["name"] for z in zones}
    assert KNOWN_ZONE in names, f"expected {KNOWN_ZONE} in {names}"


async def test_get_zone_returns_zone_config(bd_token: str) -> None:
    """`GET /zone?zone=<name>` returns config for a specific zone."""
    _ = bd_token
    resp = await bd_account_management_get_zone(zone=KNOWN_ZONE)
    assert not _is_error(resp), f"unexpected error: {resp}"
    assert "created" in resp or "plan" in resp, f"unexpected shape: {list(resp.keys())}"


async def test_get_zone_whitelist_returns_dict(bd_token: str) -> None:
    """`GET /zone/whitelist` returns mapping of zone → IP whitelist."""
    _ = bd_token
    resp = await bd_account_management_get_zone_whitelist()
    assert not _is_error(resp), f"unexpected error: {resp}"
    # Response is a dict like {"mcp_unlocker": ["any"], ...} — `error` would
    # only appear on failure, so any non-error dict is structurally valid.
    assert isinstance(resp, dict)


async def test_get_zone_blacklist_returns_dict(bd_token: str) -> None:
    """`GET /zone/blacklist` returns mapping (or empty dict if none configured)."""
    _ = bd_token
    resp = await bd_account_management_get_zone_blacklist()
    assert not _is_error(resp), f"unexpected error: {resp}"
    assert isinstance(resp, dict)


async def test_list_zone_passwords_returns_passwords_for_known_zone(bd_token: str) -> None:
    """`GET /zone/passwords?zone=<name>` returns list under `passwords` key."""
    _ = bd_token
    resp = await bd_account_management_list_zone_passwords(zone=KNOWN_ZONE)
    assert not _is_error(resp), f"unexpected error: {resp}"
    assert "passwords" in resp
    assert isinstance(resp["passwords"], list)


async def test_list_zone_permissions_returns_perms(bd_token: str) -> None:
    """`GET /zone/permissions?zone=<name>` returns the zone's enabled features."""
    _ = bd_token
    resp = await bd_account_management_list_zone_permissions(zone=KNOWN_ZONE)
    assert not _is_error(resp), f"unexpected error: {resp}"
    assert "perms" in resp
    assert isinstance(resp["perms"], list)
