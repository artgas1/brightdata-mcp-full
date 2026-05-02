"""Smoke tests for non-account_management groups against live BD API.

Strategy
--------
Free / zone-only tokens can hit a subset of groups:
- archive (web archive endpoints — read-only)
- browser_api (list sessions — works on free tier, may be empty)
- marketplace_dataset (catalogue list endpoint is public)
- account_management bandwidth/cost endpoints (already covered separately)

Paid-tier groups (skipped with `pytest.skip` + reason):
- scraping_shield (requires "Scraping Shield is enabled" — 401 otherwise)
- scrapers / serp / scraper_studio (paid scraper plans / IDE access required)
- proxy_manager (`/domains/{metric}` requires LPM tooling not in v1 scope)
- proxy / serp / unlocker_rest /req endpoints — only valid via dedicated zones
  (the test token's `mcp_unlocker` zone is a Web Unlocker, not a generic proxy)

Each test asserts on the structured response shape only; we don't make claims
about the data itself (account state can vary).
"""

from __future__ import annotations

import pytest

from tools.archive.bd_archive_get_webarchive_dump_by_dump_id import (
    bd_archive_get_webarchive_dump_by_dump_id,
)
from tools.archive.bd_archive_list_webarchive_dumps import bd_archive_list_webarchive_dumps
from tools.archive.bd_archive_list_webarchive_searches import (
    bd_archive_list_webarchive_searches,
)
from tools.browser_api.bd_browser_api_list_browser_sessions import (
    bd_browser_api_list_browser_sessions,
)
from tools.marketplace_dataset.bd_marketplace_dataset_list_datasets import (
    bd_marketplace_dataset_list_datasets,
)


def _is_error(resp: dict) -> bool:
    return "error" in resp


# Async tests opt into asyncio mode individually; sync `pytest.skip(...)` tests
# don't get the marker (would generate a "marked async but isn't" warning).
_async = pytest.mark.asyncio


# --------------------------------------------------------------------------- #
# archive                                                                     #
# --------------------------------------------------------------------------- #


@_async
async def test_archive_list_webarchive_dumps(bd_token: str) -> None:
    """`GET /webarchive/dumps` — empty list is the expected free-tier shape."""
    _ = bd_token
    resp = await bd_archive_list_webarchive_dumps()
    assert not _is_error(resp), f"unexpected error: {resp}"
    # Empty list response gets wrapped as {"data": [], "count": 0}
    assert "data" in resp
    assert isinstance(resp["data"], list)


@_async
async def test_archive_list_webarchive_searches(bd_token: str) -> None:
    """`GET /webarchive/searches` — empty list expected."""
    _ = bd_token
    resp = await bd_archive_list_webarchive_searches()
    assert not _is_error(resp), f"unexpected error: {resp}"
    assert "data" in resp
    assert isinstance(resp["data"], list)


@_async
async def test_archive_get_dump_nonexistent_returns_structured_404(bd_token: str) -> None:
    """Path-param substitution: nonexistent ID → structured 404 from BD API."""
    _ = bd_token
    resp = await bd_archive_get_webarchive_dump_by_dump_id(dump_id="def_not_a_real_id")
    assert _is_error(resp)
    assert resp["status_code"] == 404
    # BD returns {"error": "Dump not found", "error_code": "not_found"} as details.
    details = resp.get("details", {})
    if isinstance(details, dict):
        assert "not" in str(details).lower()


# --------------------------------------------------------------------------- #
# browser_api                                                                 #
# --------------------------------------------------------------------------- #


@_async
async def test_browser_api_list_sessions(bd_token: str) -> None:
    """`GET /browser_sessions` — returns paginated structure even when empty."""
    _ = bd_token
    resp = await bd_browser_api_list_browser_sessions()
    assert not _is_error(resp), f"unexpected error: {resp}"
    # BD wraps in {"sessions": [...], "count": N, "total": N, "pagination": {...}}
    assert "sessions" in resp
    assert "pagination" in resp
    assert isinstance(resp["sessions"], list)


# --------------------------------------------------------------------------- #
# marketplace_dataset                                                         #
# --------------------------------------------------------------------------- #


@_async
async def test_marketplace_dataset_list_datasets(bd_token: str) -> None:
    """`GET /datasets/list` returns BD's public dataset catalogue (~hundreds)."""
    _ = bd_token
    resp = await bd_marketplace_dataset_list_datasets()
    assert not _is_error(resp), f"unexpected error: {resp}"
    assert "data" in resp
    assert resp["count"] > 10, f"expected >10 datasets, got {resp.get('count')}"
    # Sanity-check the shape of a dataset entry.
    sample = resp["data"][0]
    assert "id" in sample and sample["id"].startswith("gd_")
    assert "name" in sample


# --------------------------------------------------------------------------- #
# Paid-tier groups — skipped with reason                                      #
# --------------------------------------------------------------------------- #


@_async
async def test_scraping_shield_requires_paid_plan(bd_token: str) -> None:
    """Documents that scraping_shield endpoints return 401 without paid plan.

    We don't `xfail` — we assert the EXPECTED 401 to catch silent regressions
    where BD changes the error code or where our test token suddenly gains
    Scraping Shield access (which would require updating this test).
    """
    _ = bd_token
    from tools.scraping_shield.bd_scraping_shield_list_shield_class import (
        bd_scraping_shield_list_shield_class,
    )

    resp = await bd_scraping_shield_list_shield_class()
    if not _is_error(resp):
        pytest.skip("Scraping Shield unexpectedly enabled on this token — update test")
    assert resp["status_code"] == 401
    assert "shield" in str(resp.get("details", "")).lower() or "shield" in resp["error"].lower()


def test_scrapers_group_skipped_for_paid_tier() -> None:
    """scrapers tools call /datasets/v3/trigger with dataset_id — needs paid plan.

    The endpoint exists but submitting a job costs money. We verify only that
    the tool function is importable and exposes the expected signature.
    """
    from tools.scrapers.bd_scrapers_create_datasets_v3_trigger import (
        bd_scrapers_create_datasets_v3_trigger,
    )

    assert callable(bd_scrapers_create_datasets_v3_trigger)
    pytest.skip(
        "scrapers/* tools cost credits per call — covered by import + write-gate tests only"
    )


def test_serp_group_skipped_for_paid_tier() -> None:
    """SERP /req endpoints require a SERP-type zone, not the test account's Web Unlocker."""
    from tools.serp.bd_serp_create_request import bd_serp_create_request

    assert callable(bd_serp_create_request)
    pytest.skip("serp/* tools require a SERP-type zone — not provisioned on test account")


def test_scraper_studio_group_skipped_for_paid_tier() -> None:
    """Scraper Studio (DCA) requires the Web Scraper IDE to be enabled."""
    from tools.scraper_studio.bd_scraper_studio_create_dca_collector import (
        bd_scraper_studio_create_dca_collector,
    )

    assert callable(bd_scraper_studio_create_dca_collector)
    pytest.skip("scraper_studio/* requires Web Scraper IDE access — not on test plan")


def test_proxy_manager_group_skipped_self_hosted() -> None:
    """proxy_manager wraps the LPM (Local Proxy Manager) tool — needs LPM running."""
    from tools.proxy_manager.bd_proxy_manager_get_domain_metrics import (
        bd_proxy_manager_get_domain_metrics,
    )

    assert callable(bd_proxy_manager_get_domain_metrics)
    pytest.skip("proxy_manager/* requires self-hosted LPM — out of scope for live smoke")


def test_video_downloader_group_skipped_paid() -> None:
    """video_downloader posts to /video/trigger — costs per-video credits."""
    from tools.video_downloader.bd_video_downloader_trigger_video_download import (
        bd_video_downloader_trigger_video_download,
    )

    assert callable(bd_video_downloader_trigger_video_download)
    pytest.skip("video_downloader/* costs credits per video — write-gated, smoke skipped")
