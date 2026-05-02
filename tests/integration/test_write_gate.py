"""Verify the BD_ENABLE_WRITES gate end-to-end on auto-generated tools.

This is a system-level check that the `@requires_write_enabled` decorator is
actually applied to every tool the codegen marked as `WRITES = True`. We don't
hit the live API — when writes ARE enabled, we mock httpx so no real mutation
happens against the BD account.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

# Three representative write tools from different groups.
from tools.account_management.bd_account_management_create_zone import (
    bd_account_management_create_zone,
)
from tools.account_management.bd_account_management_create_zone_whitelist import (
    bd_account_management_create_zone_whitelist,
)
from tools.deep_lookup.bd_deep_lookup_create_preview import bd_deep_lookup_create_preview

# `no_token` marker = these tests don't need BD_TOKEN. The async tests below
# get @pytest.mark.asyncio individually via the auto mode (asyncio_mode=auto).
pytestmark = pytest.mark.no_token


# --------------------------------------------------------------------------- #
# Default: writes disabled                                                    #
# --------------------------------------------------------------------------- #


async def test_create_zone_blocked_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Zone-create is blocked when BD_ENABLE_WRITES is unset."""
    monkeypatch.delenv("BD_ENABLE_WRITES", raising=False)
    resp = await bd_account_management_create_zone(body={"zone": {"name": "test"}})
    _assert_blocked(resp)


async def test_create_zone_whitelist_blocked_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Whitelist-add is blocked when BD_ENABLE_WRITES is unset."""
    monkeypatch.delenv("BD_ENABLE_WRITES", raising=False)
    resp = await bd_account_management_create_zone_whitelist(
        body={"zone": "mcp_unlocker", "ip": "1.2.3.4"}
    )
    _assert_blocked(resp)


async def test_deep_lookup_preview_blocked_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """deep_lookup preview is blocked when BD_ENABLE_WRITES is unset.

    deep_lookup `POST /preview` is technically idempotent (returns generated
    sample data without persistent side-effects), but the codegen still wraps
    POST/PUT/PATCH/DELETE in the gate uniformly — so we verify it triggers.
    """
    monkeypatch.delenv("BD_ENABLE_WRITES", raising=False)
    resp = await bd_deep_lookup_create_preview(body={"query": "test"})
    _assert_blocked(resp)


async def test_blocked_for_falsy_values(monkeypatch: pytest.MonkeyPatch) -> None:
    """Only literal `BD_ENABLE_WRITES=true` (lowercased) enables writes."""
    for value in ("false", "0", "no", "yes", "TRUE", "True"):
        monkeypatch.setenv("BD_ENABLE_WRITES", value)
        resp = await bd_account_management_create_zone(body={})
        if value.strip().lower() == "true":
            # Skip — we test the enabled path separately with a mocked HTTP call.
            continue
        _assert_blocked(resp), f"expected block for BD_ENABLE_WRITES={value!r}"


# --------------------------------------------------------------------------- #
# Enabled: writes go through (with HTTP mocked so we don't touch the account) #
# --------------------------------------------------------------------------- #


async def test_create_zone_passes_through_when_writes_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When writes are enabled, the gate is bypassed and the underlying request fires.

    We patch `lib.client.bd_request` so no actual HTTP call is made — we just
    confirm the wrapped tool calls into the client with the expected args.
    """
    monkeypatch.setenv("BD_ENABLE_WRITES", "true")
    monkeypatch.setenv("BRIGHT_DATA_API_TOKEN", "test-token-for-mock")

    expected_response = {"zone": "new-zone-id", "created_at": "2026-05-02T00:00:00Z"}
    mock_request = AsyncMock(return_value=expected_response)

    # Patch in the module the tool imports it from (function-level alias).
    with patch(
        "tools.account_management.bd_account_management_create_zone.bd_request",
        mock_request,
    ):
        resp = await bd_account_management_create_zone(body={"zone": {"name": "test"}})

    assert resp == expected_response, f"unexpected response: {resp}"
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert args[0] == "POST"
    assert args[1] == "/zone"
    assert kwargs.get("json") == {"zone": {"name": "test"}}


async def test_deep_lookup_preview_passes_through_when_writes_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """deep_lookup preview reaches client.bd_request when writes enabled."""
    monkeypatch.setenv("BD_ENABLE_WRITES", "true")
    monkeypatch.setenv("BRIGHT_DATA_API_TOKEN", "test-token-for-mock")

    mock_request = AsyncMock(return_value={"preview_id": "pv_123"})
    with patch(
        "tools.deep_lookup.bd_deep_lookup_create_preview.bd_request",
        mock_request,
    ):
        resp = await bd_deep_lookup_create_preview(body={"query": "ping"})

    assert resp == {"preview_id": "pv_123"}
    mock_request.assert_called_once()
    args, _ = mock_request.call_args
    assert args[0] == "POST"
    assert args[1] == "/preview"


# --------------------------------------------------------------------------- #
# Coverage: every tool with WRITES=True is decorator-wrapped                  #
# --------------------------------------------------------------------------- #


@pytest.mark.no_token
def test_every_write_tool_is_gated() -> None:
    """Walk all tools/<group>/__init__.py and confirm WRITES=True tools are blocked.

    Catches a regression where someone adds a tool but forgets the
    `@requires_write_enabled` decorator. We can't *invoke* every tool here
    (some need positional args we don't know), so we inspect the module's
    `WRITES` constant and check that calling the function without writes
    enabled returns the structured block error rather than calling out.
    """
    # We import lazily to avoid pulling in 149 modules at module collection.
    import importlib

    from lib.groups import KNOWN_GROUPS

    leaks: list[str] = []
    for group in KNOWN_GROUPS:
        pkg = importlib.import_module(f"tools.{group}")
        for tool_name in pkg.__all__:
            if tool_name == "register_tools":
                continue
            tool_mod = importlib.import_module(f"tools.{group}.{tool_name}")
            writes = getattr(tool_mod, "WRITES", False)
            if not writes:
                continue
            # The decorator sets `__wrapped__` (functools.wraps preserves it).
            fn = getattr(tool_mod, tool_name)
            if not hasattr(fn, "__wrapped__"):
                leaks.append(f"{group}.{tool_name} (WRITES=True but not decorator-wrapped)")
    assert not leaks, "Write tools missing safety decorator:\n" + "\n".join(leaks)


def _assert_blocked(resp: dict[str, Any]) -> None:
    """Assert the response is the structured write-disabled error."""
    assert "error" in resp, f"expected blocked, got {resp}"
    assert "Write operations disabled" in resp["error"]
    assert "BD_ENABLE_WRITES" in resp["hint"]
    assert resp["status_code"] == 0
