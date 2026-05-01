"""Async HTTP client for Bright Data API.

Wraps httpx with bearer auth, retry on 5xx/timeouts, and structured error returns
(no HTTP exceptions raised — tools return dicts that MCP can serialize).
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

BD_API_BASE = "https://api.brightdata.com"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3


class BrightDataAuthError(Exception):
    """Raised when BRIGHT_DATA_API_TOKEN is missing."""


def _get_token() -> str:
    token = os.environ.get("BRIGHT_DATA_API_TOKEN", "").strip()
    if not token:
        raise BrightDataAuthError(
            "BRIGHT_DATA_API_TOKEN env var is required. "
            "Get one from https://brightdata.com/cp/setting/users"
        )
    return token


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_get_token()}",
        "Accept": "application/json",
        "User-Agent": "brightdata-mcp-full/0.1.0",
    }


def _is_retryable_status(status: int) -> bool:
    """5xx and 429 are retryable. 4xx (other) are not — caller error."""
    return status >= 500 or status == 429


class _RetryableHTTPError(Exception):
    """Internal sentinel raised inside retry loop to trigger retry."""


async def bd_request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json: Any | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> dict[str, Any]:
    """Make an authenticated request to Bright Data API with retry.

    Returns either the parsed response body (dict) or a structured error dict:
    `{"error": str, "status_code": int}` for 4xx errors and exhausted retries.

    Args:
        method: HTTP verb (GET, POST, PUT, DELETE).
        path: API path starting with `/` (joined to https://api.brightdata.com).
        params: Optional query string params.
        json: Optional JSON body for POST/PUT.
        timeout: Request timeout in seconds.
        max_retries: Number of attempts (default 3) — only on retryable failures.

    Returns:
        Parsed JSON response (dict or list wrapped in `{"data": ...}`),
        or `{"error": str, "status_code": int, "details": Any}` on failure.
    """
    url = f"{BD_API_BASE}{path}"

    try:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type(
                (_RetryableHTTPError, httpx.TimeoutException, httpx.NetworkError)
            ),
            reraise=True,
        ):
            with attempt:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.request(
                        method=method.upper(),
                        url=url,
                        headers=_headers(),
                        params=params,
                        json=json,
                    )

                # Retryable: trigger retry
                if _is_retryable_status(response.status_code):
                    raise _RetryableHTTPError(
                        f"{response.status_code} on {method} {path}: {response.text[:200]}"
                    )

                # Non-retryable error: return structured error
                if response.status_code >= 400:
                    return _structured_error(response)

                # Success: parse body
                return _parse_response(response)
    except BrightDataAuthError as e:
        return {"error": str(e), "status_code": 0}
    except _RetryableHTTPError as e:
        return {
            "error": f"Request failed after {max_retries} attempts: {e}",
            "status_code": 503,
        }
    except httpx.TimeoutException as e:
        return {"error": f"Request timed out: {e}", "status_code": 0}
    except httpx.NetworkError as e:
        return {"error": f"Network error: {e}", "status_code": 0}

    # Unreachable, but mypy/pyright satisfaction
    return {"error": "Unknown error in bd_request control flow", "status_code": 0}


def _structured_error(response: httpx.Response) -> dict[str, Any]:
    """Build structured error dict from a 4xx response."""
    body_preview: Any
    try:
        body_preview = response.json()
    except Exception:
        body_preview = response.text[:500]
    return {
        "error": f"HTTP {response.status_code} on {response.request.method} "
        f"{response.request.url.path}",
        "status_code": response.status_code,
        "details": body_preview,
    }


def _parse_response(response: httpx.Response) -> dict[str, Any]:
    """Parse a successful response body. Wrap list responses under 'data'."""
    if not response.content:
        return {"status_code": response.status_code}
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            parsed = response.json()
        except Exception:
            return {"status_code": response.status_code, "raw": response.text[:1000]}
        if isinstance(parsed, list):
            return {"data": parsed, "count": len(parsed)}
        if isinstance(parsed, dict):
            return parsed
        return {"data": parsed}
    # Non-JSON body — return as text
    return {"status_code": response.status_code, "text": response.text[:5000]}


# Convenience verb wrappers
async def bd_get(
    path: str, *, params: dict[str, Any] | None = None, timeout: float = DEFAULT_TIMEOUT
) -> dict[str, Any]:
    return await bd_request("GET", path, params=params, timeout=timeout)


async def bd_post(
    path: str, *, json: Any | None = None, timeout: float = DEFAULT_TIMEOUT
) -> dict[str, Any]:
    return await bd_request("POST", path, json=json, timeout=timeout)


async def bd_put(
    path: str, *, json: Any | None = None, timeout: float = DEFAULT_TIMEOUT
) -> dict[str, Any]:
    return await bd_request("PUT", path, json=json, timeout=timeout)


async def bd_delete(
    path: str, *, params: dict[str, Any] | None = None, timeout: float = DEFAULT_TIMEOUT
) -> dict[str, Any]:
    return await bd_request("DELETE", path, params=params, timeout=timeout)
