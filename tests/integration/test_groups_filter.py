"""Verify the `GROUPS` env var loads exactly the requested groups.

Strategy
--------
We exercise `server._register_group` and `lib.groups.{load_groups_from_env,
expand_wildcard}` directly rather than launching a subprocess — same logic,
much faster, and lets us assert on the count of registered tools per call.
"""

from __future__ import annotations

import importlib

import pytest
from fastmcp import FastMCP

import server
from lib.groups import KNOWN_GROUPS, expand_wildcard, load_groups_from_env

pytestmark = pytest.mark.no_token


def _fresh_mcp(name: str) -> FastMCP:
    return FastMCP(name)


def test_groups_unset_loads_account_management_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default behaviour: no env var → only `account_management`."""
    monkeypatch.delenv("GROUPS", raising=False)
    groups = expand_wildcard(load_groups_from_env())
    assert groups == ["account_management"]


def test_groups_single_account_management_loads_only_that_group(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`GROUPS=account_management` registers ONLY account tools, no other group."""
    monkeypatch.setenv("GROUPS", "account_management")
    monkeypatch.setenv("BRIGHT_DATA_API_TOKEN", "test-not-used")

    groups = expand_wildcard(load_groups_from_env())
    assert groups == ["account_management"]

    mcp = _fresh_mcp("test-acc")
    server.mcp = mcp  # swap in fresh instance
    count = server._register_group("account_management")
    assert count >= 60, f"expected >=60 account tools, got {count}"


def test_groups_wildcard_loads_all_known_groups(monkeypatch: pytest.MonkeyPatch) -> None:
    """`GROUPS=*` (or `all`) expands to every group in KNOWN_GROUPS."""
    monkeypatch.setenv("GROUPS", "*")
    groups = expand_wildcard(load_groups_from_env())
    assert groups == list(KNOWN_GROUPS)
    assert len(groups) == 15


def test_groups_all_alias_loads_all(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROUPS", "all")
    assert expand_wildcard(load_groups_from_env()) == list(KNOWN_GROUPS)


def test_groups_combination_loads_only_listed(monkeypatch: pytest.MonkeyPatch) -> None:
    """`GROUPS=archive,browser_api` registers ONLY those two groups."""
    monkeypatch.setenv("GROUPS", "archive,browser_api")
    groups = expand_wildcard(load_groups_from_env())
    assert groups == ["archive", "browser_api"]

    mcp = _fresh_mcp("test-combo")
    server.mcp = mcp
    archive_count = server._register_group("archive")
    browser_count = server._register_group("browser_api")
    assert archive_count == 6, f"archive should have 6 tools, got {archive_count}"
    assert browser_count == 2, f"browser_api should have 2 tools, got {browser_count}"


def test_groups_unknown_raises_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unknown GROUPS value raises UnknownGroupError with the bad name."""
    monkeypatch.setenv("GROUPS", "this_group_does_not_exist")
    from lib.groups import UnknownGroupError

    with pytest.raises(UnknownGroupError) as exc_info:
        load_groups_from_env()
    assert "this_group_does_not_exist" in str(exc_info.value)


def test_total_tools_via_wildcard_matches_per_group_sum(monkeypatch: pytest.MonkeyPatch) -> None:
    """Wildcard load = sum of per-group exports. No silent dropouts during dynamic loading."""
    monkeypatch.setenv("GROUPS", "*")
    groups = expand_wildcard(load_groups_from_env())

    per_group_total = 0
    for group in groups:
        module = importlib.import_module(f"tools.{group}")
        per_group_total += sum(1 for n in module.__all__ if n != "register_tools")

    # Run the same load through `_register_group` and tally the counts.
    mcp = _fresh_mcp("test-wildcard")
    server.mcp = mcp
    server_total = sum(server._register_group(g) for g in groups)

    assert server_total == per_group_total, (
        f"server registered {server_total} but groups expose {per_group_total}"
    )
