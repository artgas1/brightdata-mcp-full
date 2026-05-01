"""Unit tests for lib.safety — write-gate decorator."""

from __future__ import annotations

from typing import Any

import pytest

from lib.safety import requires_write_enabled, writes_enabled


@pytest.mark.asyncio
async def test_writes_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BD_ENABLE_WRITES", raising=False)
    assert writes_enabled() is False


@pytest.mark.asyncio
async def test_writes_enabled_when_true(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BD_ENABLE_WRITES", "true")
    assert writes_enabled() is True


@pytest.mark.asyncio
async def test_writes_disabled_for_other_values(monkeypatch: pytest.MonkeyPatch) -> None:
    for v in ("", "false", "0", "no", "TRUE ", "True"):
        monkeypatch.setenv("BD_ENABLE_WRITES", v)
        # Only literal lower-case "true" enables (after .strip().lower())
        if v.strip().lower() == "true":
            assert writes_enabled() is True, f"expected True for {v!r}"
        else:
            assert writes_enabled() is False, f"expected False for {v!r}"


@pytest.mark.asyncio
async def test_decorator_blocks_when_writes_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("BD_ENABLE_WRITES", raising=False)

    called = False

    @requires_write_enabled
    async def my_write_tool(name: str) -> dict[str, Any]:
        nonlocal called
        called = True
        return {"created": name}

    result = await my_write_tool("test-zone")
    assert called is False
    assert "Write operations disabled" in result["error"]
    assert "BD_ENABLE_WRITES" in result["hint"]


@pytest.mark.asyncio
async def test_decorator_allows_when_writes_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("BD_ENABLE_WRITES", "true")

    @requires_write_enabled
    async def my_write_tool(name: str) -> dict[str, Any]:
        return {"created": name}

    result = await my_write_tool("test-zone")
    assert result == {"created": "test-zone"}


@pytest.mark.asyncio
async def test_decorator_preserves_function_metadata() -> None:
    @requires_write_enabled
    async def some_tool(name: str) -> dict[str, Any]:
        """Original docstring."""
        return {"ok": name}

    assert some_tool.__name__ == "some_tool"
    assert some_tool.__doc__ == "Original docstring."
