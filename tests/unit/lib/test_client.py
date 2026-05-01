"""Unit tests for lib.client — async HTTP client with retry and structured errors.

We mock httpx by injecting a transport via `httpx.MockTransport` is not used
here; instead we monkey-patch `httpx.AsyncClient` to return scripted responses.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from lib import client as bd_client


@pytest.fixture(autouse=True)
def _set_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BRIGHT_DATA_API_TOKEN", "test-token-abc")


class _FakeResponse:
    """Minimal stand-in for httpx.Response covering the attrs bd_request reads."""

    def __init__(
        self,
        status_code: int,
        json_body: Any | None = None,
        text: str = "",
        content_type: str = "application/json",
        method: str = "GET",
        path: str = "/test",
    ) -> None:
        self.status_code = status_code
        self._json = json_body
        self.text = text or (str(json_body) if json_body is not None else "")
        self.headers = {"content-type": content_type}
        self.content = self.text.encode() if self.text else b""

        class _Req:
            def __init__(self, m: str, p: str) -> None:
                self.method = m
                self.url = httpx.URL(f"https://api.brightdata.com{p}")

        self.request = _Req(method, path)

    def json(self) -> Any:
        if self._json is None:
            raise ValueError("no json")
        return self._json


def _make_client_factory(responses: list[_FakeResponse]):
    """Return a context-manager class that pops responses sequentially."""
    queue = list(responses)

    class _FakeAsyncClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> _FakeAsyncClient:
            return self

        async def __aexit__(self, *args: Any) -> None:
            return None

        async def request(self, **kwargs: Any) -> _FakeResponse:
            if not queue:
                raise AssertionError("more requests than scripted responses")
            return queue.pop(0)

    return _FakeAsyncClient


@pytest.mark.asyncio
async def test_get_returns_dict_on_200(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _make_client_factory(
        [_FakeResponse(200, json_body={"balance": 12.34, "pending_balance": 5.0})]
    )
    monkeypatch.setattr(bd_client.httpx, "AsyncClient", fake)

    result = await bd_client.bd_get("/customer/balance")
    assert result == {"balance": 12.34, "pending_balance": 5.0}


@pytest.mark.asyncio
async def test_get_wraps_list_response_in_data(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _make_client_factory([_FakeResponse(200, json_body=[{"name": "z1"}, {"name": "z2"}])])
    monkeypatch.setattr(bd_client.httpx, "AsyncClient", fake)

    result = await bd_client.bd_get("/zone/get_active_zones")
    assert result == {"data": [{"name": "z1"}, {"name": "z2"}], "count": 2}


@pytest.mark.asyncio
async def test_get_returns_structured_error_on_404(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _make_client_factory([_FakeResponse(404, text="Not found", content_type="text/plain")])
    monkeypatch.setattr(bd_client.httpx, "AsyncClient", fake)

    result = await bd_client.bd_get("/missing")
    assert result["status_code"] == 404
    assert "HTTP 404" in result["error"]
    assert result["details"] == "Not found"


@pytest.mark.asyncio
async def test_get_returns_structured_error_on_403(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _make_client_factory([_FakeResponse(403, text="Forbidden", content_type="text/plain")])
    monkeypatch.setattr(bd_client.httpx, "AsyncClient", fake)

    result = await bd_client.bd_get("/customer/balance")
    assert result["status_code"] == 403
    assert "HTTP 403" in result["error"]


@pytest.mark.asyncio
async def test_retry_on_5xx_then_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """503 should retry and eventually succeed on 200."""
    fake = _make_client_factory(
        [
            _FakeResponse(503, text="overloaded", content_type="text/plain"),
            _FakeResponse(503, text="overloaded", content_type="text/plain"),
            _FakeResponse(200, json_body={"ok": True}),
        ]
    )
    monkeypatch.setattr(bd_client.httpx, "AsyncClient", fake)

    # Speed up the retry — replace tenacity sleep
    import asyncio

    async def _no_sleep(_seconds: float) -> None:
        return None

    monkeypatch.setattr(asyncio, "sleep", _no_sleep)

    result = await bd_client.bd_get("/test")
    assert result == {"ok": True}


@pytest.mark.asyncio
async def test_retry_exhausted_returns_503_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """All 3 attempts fail with 5xx → return error dict, don't raise."""
    fake = _make_client_factory(
        [
            _FakeResponse(503, text="boom", content_type="text/plain"),
            _FakeResponse(503, text="boom", content_type="text/plain"),
            _FakeResponse(503, text="boom", content_type="text/plain"),
        ]
    )
    monkeypatch.setattr(bd_client.httpx, "AsyncClient", fake)

    import asyncio

    async def _no_sleep(_seconds: float) -> None:
        return None

    monkeypatch.setattr(asyncio, "sleep", _no_sleep)

    result = await bd_client.bd_get("/test")
    assert result["status_code"] == 503
    assert "after" in result["error"].lower()


@pytest.mark.asyncio
async def test_4xx_does_not_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    """400 should return immediately without consuming retry budget."""
    call_count = 0

    class _CountingClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def __aenter__(self) -> _CountingClient:
            return self

        async def __aexit__(self, *args: Any) -> None:
            return None

        async def request(self, **kwargs: Any) -> _FakeResponse:
            nonlocal call_count
            call_count += 1
            return _FakeResponse(400, text="bad request", content_type="text/plain")

    monkeypatch.setattr(bd_client.httpx, "AsyncClient", _CountingClient)

    result = await bd_client.bd_get("/test")
    assert call_count == 1
    assert result["status_code"] == 400


@pytest.mark.asyncio
async def test_missing_token_returns_auth_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BRIGHT_DATA_API_TOKEN", raising=False)

    result = await bd_client.bd_get("/test")
    assert "BRIGHT_DATA_API_TOKEN" in result["error"]
    assert result["status_code"] == 0
