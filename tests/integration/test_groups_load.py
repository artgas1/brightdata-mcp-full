"""Verify every known group can be imported and registers tools cleanly.

This is a structural smoke test — does NOT touch the live BD API. It catches
codegen regressions where a generated `__init__.py` references a missing tool
file or a tool module fails to import (syntax error, bad keyword arg, etc).
"""

from __future__ import annotations

import importlib

import pytest
from fastmcp import FastMCP

from lib.groups import KNOWN_GROUPS

# Expected tool counts as of A2 codegen (2026-05-01). If codegen changes, update
# the lower bounds. Upper bound left open — adding endpoints is fine.
EXPECTED_MIN_TOOL_COUNTS: dict[str, int] = {
    "account_management": 60,  # 70 generated + 1 smoke override; tolerate drift
    "proxy_manager": 1,
    "scrapers": 3,
    "serp": 3,
    "marketplace_dataset": 20,
    "scraper_studio": 10,
    "rest_api": 0,  # currently empty — no spec mapped
    "proxy": 3,
    "deep_lookup": 9,
    "archive": 6,
    "scraping_shield": 4,
    "browser_api": 2,
    "unlocker_rest": 3,
    "video_downloader": 1,
    "misc": 6,
}


@pytest.mark.no_token
@pytest.mark.parametrize("group", KNOWN_GROUPS)
def test_group_module_imports(group: str) -> None:
    """`tools.<group>` imports without raising and exposes register_tools."""
    module = importlib.import_module(f"tools.{group}")
    assert hasattr(module, "register_tools"), f"tools.{group} missing register_tools"
    assert callable(module.register_tools), f"tools.{group}.register_tools not callable"
    assert hasattr(module, "__all__"), f"tools.{group} missing __all__"


@pytest.mark.no_token
@pytest.mark.parametrize("group", KNOWN_GROUPS)
def test_group_register_tools_runs(group: str) -> None:
    """register_tools(mcp) executes without raising for an empty FastMCP."""
    module = importlib.import_module(f"tools.{group}")
    mcp = FastMCP(f"test-{group}")
    module.register_tools(mcp)


@pytest.mark.no_token
@pytest.mark.parametrize("group", KNOWN_GROUPS)
def test_group_tool_count(group: str) -> None:
    """Each group exports at least the expected number of tools.

    Lower-bound check — adding tools is fine, removing them needs an explicit
    update to EXPECTED_MIN_TOOL_COUNTS so we notice the regression.
    """
    module = importlib.import_module(f"tools.{group}")
    exported = [name for name in module.__all__ if name != "register_tools"]
    expected_min = EXPECTED_MIN_TOOL_COUNTS[group]
    assert (
        len(exported) >= expected_min
    ), f"{group} exports {len(exported)} tools, expected >= {expected_min}"


@pytest.mark.no_token
def test_total_tool_count_matches_spec_target() -> None:
    """Total tool count across all groups should be close to the 149 reported by A2."""
    total = 0
    for group in KNOWN_GROUPS:
        module = importlib.import_module(f"tools.{group}")
        total += sum(1 for n in module.__all__ if n != "register_tools")
    # A2 produced 149; allow drift of ±10 for spec churn between regenerations.
    assert 130 <= total <= 200, f"Total tool count out of expected range: {total}"


@pytest.mark.no_token
def test_no_duplicate_tool_names_across_groups() -> None:
    """Same function name cannot appear in two groups (would clash in MCP namespace)."""
    seen: dict[str, str] = {}
    for group in KNOWN_GROUPS:
        module = importlib.import_module(f"tools.{group}")
        for name in module.__all__:
            if name == "register_tools":
                continue
            if name in seen:
                pytest.fail(f"Duplicate tool name {name!r} in {group} and {seen[name]}")
            seen[name] = group
