# Changelog

All notable changes to `brightdata-mcp-full` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] — 2026-05-04

### Fixed

- Console script `brightdata-mcp-full` failed with `ModuleNotFoundError: No
  module named 'server'` after `pip install` / `uvx`. Root cause: `server.py`
  lives at the repo root (not inside a package), and the wheel's
  `[tool.hatch.build.targets.wheel] packages = ["lib", "tools"]` pulled in
  the packages but skipped top-level modules. Added `force-include` for
  `server.py` so the entry point resolves.

## [0.1.0] — 2026-05-04

Initial release. Comprehensive Python MCP server complementing Bright Data's
official MCP — exposes account-management, proxy zones, IPs, billing,
statistics, LPM, deep-lookup, archive, scraping-shield, marketplace datasets
and other groups not covered by the official server.

### Added

- **149 auto-generated MCP tools** across **15 product groups**, derived from
  19 official Bright Data OpenAPI specifications.
- **Group-based runtime tool selection** via `GROUPS` env var. Default
  `account_management` (70 tools); supports any subset or `all`.
- **Write-gate** via `BD_ENABLE_WRITES` env var (default `false`). All
  destructive endpoints (POST/PUT/DELETE that mutate state) require explicit
  opt-in.
- **3 hand-written smoke tools** with rich Bright-Data-specific docstrings:
  `bd_account_get_status`, `bd_account_get_balance`, `bd_zones_list`.
  Marked with `# SMOKE-TOOL` to survive code regeneration.
- **Code-generation pipeline** (`lib/codegen.py`, `scripts/regenerate.py`):
  parses OpenAPI specs → emits FastMCP tool wrappers preserving smoke tools.
- **HTTP client** (`lib/client.py`): async `httpx` wrapper with bearer auth,
  exponential-backoff retry via `tenacity`, structured error envelope
  `{"error": str, "status_code": int}`.
- **28 unit tests** (client, safety, groups parsing).
- **82 integration tests** (group loading, account-management live calls,
  cross-group smoke, write-gate enforcement, GROUPS filter).
- **Documentation**: `docs/groups.md` (auto-generated tool catalog),
  `docs/auth.md`, `docs/examples.md`, `docs/troubleshooting.md`.
- **MIT license**, FastMCP transport (stdio).

### Known limits / scope

- Auto-generated tool descriptions are minimal (one-liner from OpenAPI
  `summary`). Production use of specific endpoints may benefit from
  hand-written wrappers like the smoke tools.
- Initial coverage is 149 tools from 19 OpenAPI specs. The Bright Data API
  reference advertises ~350 endpoints; the gap is mostly endpoints whose
  OpenAPI spec is not yet published. Manual wrappers for paid-tier scrapers
  (web scraper IDE, deep lookup) are a possible v1.1+ addition.
- Streaming HTTP / SSE transport not yet supported (stdio only).

[Unreleased]: https://github.com/artgas1/brightdata-mcp-full/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/artgas1/brightdata-mcp-full/releases/tag/v0.1.0
