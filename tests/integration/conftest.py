"""Pytest config for integration tests — gated on BRIGHT_DATA_API_TOKEN env var.

Integration tests hit the live Bright Data API. They are skipped automatically
when the token isn't set so unit-only CI runs aren't blocked.
"""

from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="session")
def bd_token() -> str:
    token = os.environ.get("BRIGHT_DATA_API_TOKEN", "").strip()
    if not token:
        pytest.skip("BRIGHT_DATA_API_TOKEN env not set — skipping integration tests")
    return token
