"""Parse the GROUPS env var and select which tool packages to load.

Groups correspond to Bright Data product areas (account_management, proxy_manager,
scrapers, etc.). Loading is per-group so users can keep MCP context small —
default `account_management` registers ~44 tools, while `*` or `all` loads everything.
"""

from __future__ import annotations

import os

KNOWN_GROUPS = (
    "account_management",
    "proxy_manager",
    "scrapers",
    "serp",
    "marketplace_dataset",
    "scraper_studio",
    "rest_api",
    "proxy",
    "deep_lookup",
    "archive",
    "scraping_shield",
    "browser_api",
    "unlocker_rest",
    "video_downloader",
    "misc",
)

DEFAULT_GROUPS: tuple[str, ...] = ("account_management",)
WILDCARD_SENTINEL = "*"


class UnknownGroupError(ValueError):
    """Raised when GROUPS contains a name not in KNOWN_GROUPS."""


def load_groups_from_env() -> list[str]:
    """Read the `GROUPS` env var and return the list of groups to load.

    Behavior:
        - Unset or empty → returns `list(DEFAULT_GROUPS)` (= `["account_management"]`).
        - `*` or `all` (case-insensitive) → returns `["*"]` sentinel meaning "load all".
        - Comma-separated list → parsed, trimmed, validated against KNOWN_GROUPS.
        - Unknown group name raises UnknownGroupError.

    Returns:
        List of group identifiers, or `["*"]` for all-known.
    """
    raw = os.environ.get("GROUPS", "").strip()
    if not raw:
        return list(DEFAULT_GROUPS)

    # Wildcard
    if raw.lower() in ("*", "all"):
        return [WILDCARD_SENTINEL]

    # Parse comma-separated
    groups = [g.strip() for g in raw.split(",") if g.strip()]
    if not groups:
        return list(DEFAULT_GROUPS)

    # Validate
    unknown = [g for g in groups if g not in KNOWN_GROUPS]
    if unknown:
        raise UnknownGroupError(f"Unknown group(s): {unknown}. Known groups: {list(KNOWN_GROUPS)}")

    # Deduplicate while preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for g in groups:
        if g not in seen:
            seen.add(g)
            deduped.append(g)
    return deduped


def expand_wildcard(groups: list[str]) -> list[str]:
    """Resolve the `["*"]` sentinel to all KNOWN_GROUPS. No-op otherwise."""
    if groups == [WILDCARD_SENTINEL]:
        return list(KNOWN_GROUPS)
    return groups
