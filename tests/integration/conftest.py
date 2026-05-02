"""Pytest config for integration tests — gated on BRIGHT_DATA_API_TOKEN env var.

Integration tests hit the live Bright Data API. They are skipped automatically
when the token isn't set so unit-only CI runs aren't blocked.

Test policy
-----------

- Only read-only endpoints are exercised live. Write tools are validated through
  the write-gate (see test_write_gate.py) and never actually mutate the account.
- Endpoints that require a paid plan (Scraping Shield, premium scrapers, SERP)
  are wrapped with `pytest.mark.xfail(strict=False)` so the suite stays green
  on a free/zone-only token but still surfaces unexpected regressions.
- Live tests should run in <30s total — keep them sparse and use the shared
  client to avoid burning rate limits.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest


def _token() -> str | None:
    raw = os.environ.get("BRIGHT_DATA_API_TOKEN", "").strip()
    return raw or None


# Auto-mark every test in this dir as `integration`. The marker is declared in
# pyproject.toml — `pytest -m "not integration"` excludes the live suite.
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    _ = config
    for item in items:
        if "tests/integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def bd_token() -> str:
    """Provide the Bright Data API token, skipping the test if missing."""
    token = _token()
    if not token:
        pytest.skip("BRIGHT_DATA_API_TOKEN env not set — skipping integration tests")
    return token


@pytest.fixture(autouse=True)
def _ensure_token(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> None:
    """Ensure tools see the BD token via env. Skip the test if not configured.

    We deliberately use the env var (vs an injected client) because every tool
    reads the token from `lib.client._get_token()` at call time. This keeps the
    test's view of the world identical to a real MCP request.
    """
    # Skip cleanly for tests that don't need live API access.
    if "no_token" in request.keywords:
        return
    token = _token()
    if not token:
        pytest.skip("BRIGHT_DATA_API_TOKEN env not set")
    monkeypatch.setenv("BRIGHT_DATA_API_TOKEN", token)


@pytest.fixture
async def bd_client() -> AsyncIterator[None]:
    """Yield a no-op context — bd_request creates its own httpx.AsyncClient per call.

    Provided as a fixture for future expansion (e.g. shared client with caching).
    """
    yield None


# Common known-good zone names for live read-only tests.
# The test BD account (hl_15dcea24, 2026-05-01) has these two pre-provisioned zones.
KNOWN_ZONE = "mcp_unlocker"
KNOWN_BROWSER_ZONE = "mcp_browser"
