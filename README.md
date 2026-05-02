# brightdata-mcp-full

> Comprehensive Python MCP server wrapping Bright Data's REST API — **149 tools across 15 product groups**, auto-generated from 19 OpenAPI specs.

[![status](https://img.shields.io/badge/status-v0.1--alpha-yellow)](./SPEC.md)
[![license](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![python](https://img.shields.io/badge/python-3.13+-blue)](#)

## Why this exists

[Bright Data's official MCP server](https://github.com/brightdata/brightdata-mcp) is excellent — 60+ tools focused on **scraping and web access**. But Bright Data's REST API is much larger: account management, proxy zones, IPs, billing, statistics, the LPM proxy manager, deep lookup, archive API, scraping shield, marketplace datasets, and more.

**`brightdata-mcp-full` complements the official MCP** by exposing everything else as a standalone, group-organized MCP server. Run them side by side:

```jsonc
// .mcp.json
{
  "mcpServers": {
    "brightdata":      { "url": "https://mcp.brightdata.com/mcp?token=..." },        // official: scraping
    "brightdata-full": { "command": "uv", "args": ["run", "python", "server.py"] }   // this: everything else
  }
}
```

## Status

**v0.1-alpha.** Codegen pipeline merged, 149 tools generated, integration QA in progress (Round 5 of multi-agent build). See [`SPEC.md`](./SPEC.md) → "Reality Check" for the gap between the original spec estimate (350 tools) and the actual surface BD ships publicly (149 unique REST operations after dedup).

## Tool groups

| Group | Tools | Source OpenAPI specs |
|---|---:|---|
| `account_management` | 70 | `openapi`, `openapi-reseller` |
| `marketplace_dataset` | 25 | `dca-api`, `datasets-rest-api` |
| `scraper_studio` | 13 | `web-scraper-ide-rest-api` |
| `deep_lookup` | 9 | `deep-lookup` |
| `archive` | 6 | `web-archive-api` |
| `misc` | 6 | `async-api-reference`, `filter-csv-json`, `dca-custom-inputs` |
| `scraping_shield` | 4 | `scraping-shield-rest-api` |
| `scrapers` | 3 | `scraper-rest-api`, `crawl-rest-api` |
| `serp` | 3 | `serp-rest-api` |
| `proxy` | 3 | `proxy-rest-api` |
| `unlocker_rest` | 3 | `unlocker-rest-api` |
| `browser_api` | 2 | `browser-api` |
| `proxy_manager` | 1 | `proxy-manager` |
| `video_downloader` | 1 | `video-downloader` |
| `rest_api` | 0 | (no spec mapped — endpoints absorbed into `account_management`) |
| **Total** | **149** | 19 specs |

Full per-tool catalog: [`docs/groups.md`](./docs/groups.md). Auto-generated, regenerable via `uv run python scripts/generate_groups_doc.py > docs/groups.md`.

## What's covered, what's not

**Covered (149 tools):** every public REST operation BD ships in their English-language OpenAPI specs — account/zone/IP management, deep lookup, web archive, marketplace datasets, scraping shield, generic scrapers/SERP/proxy/unlocker REST endpoints, browser API session management, video downloader.

**Not covered:**
- **Per-platform scrapers** (Amazon, LinkedIn, Instagram, TikTok, Reddit, ...) — BD doesn't ship per-platform OpenAPI specs publicly. The generic `bd_scrapers_*` (3 tools) cover the trigger/snapshot pattern; per-platform discovery happens via dataset IDs.
- **SERP engine variants** (one tool per engine) — BD exposes a single generic `bd_serp_create_request` that takes engine as a parameter; not 68 separate engines.
- **LPM (Local Proxy Manager) deep features** — most LPM controls are CLI flags, not REST endpoints. The single `proxy_manager` tool covers what's exposed via REST.
- **Native proxy access** (`brd-customer-...:zone-...:password@brd.superproxy.io:33335`) — out of scope for an MCP wrapper. Use BD's proxy SDK or your HTTP client's proxy settings.
- **Browser API WebSocket** (`wss://brd.superproxy.io:9222`) — consumed by Playwright/Puppeteer directly. The MCP exposes only the REST management endpoints (`bd_browser_api_*`).
- **Scraping/AI tools already in BD's official MCP** (`web_data_*`, `scraping_browser_*`, `search_engine`, ...) — intentionally not duplicated. Run both servers side by side.

If BD ships new public OpenAPI specs, regenerate via `uv run python scripts/regenerate.py` to pick them up.

## Design highlights

- **Auto-generated from 19 OpenAPI specs** — `uv run python scripts/regenerate.py` to refresh tools when BD's API changes
- **Group-based runtime selection** via `GROUPS=` env var (default: `account_management`) — keeps Claude's context lean
- **Write-gate via `BD_ENABLE_WRITES=true`** — read-only by default for safety; explicit opt-in for ops that create/delete/modify resources
- **Zero magic** — every tool is plain Python with typed args and `bd_request` HTTP client; easy to read/audit in `tools/<group>/`
- **Stdio MCP** in v1, hosted HTTP/SSE planned for v2

## Quick start (alpha)

```bash
git clone https://github.com/artgas1/brightdata-mcp-full
cd brightdata-mcp-full
uv sync
export BRIGHT_DATA_API_TOKEN=your_token
uv run python server.py   # stdio MCP server
```

Wire into Claude Code (or Claude Desktop / Cursor):

```jsonc
{
  "mcpServers": {
    "brightdata-full": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/brightdata-mcp-full", "python", "server.py"],
      "env": {
        "BRIGHT_DATA_API_TOKEN": "your-token-here",
        "GROUPS": "account_management,deep_lookup",
        "BD_ENABLE_WRITES": "false"
      }
    }
  }
}
```

For more recipes see [`docs/examples.md`](./docs/examples.md). For auth/token setup: [`docs/auth.md`](./docs/auth.md). When something breaks: [`docs/troubleshooting.md`](./docs/troubleshooting.md).

## Roadmap

- [x] Spec approved
- [x] Scaffolding (FastMCP, lib/client, lib/safety, 3 smoke tools) — Round 1
- [x] Codegen pipeline + 149 tools auto-generated — Round 2
- [ ] Integration QA (live API smoke per group) — Round 3 (in progress)
- [x] Docs polish (this PR) — Round 5
- [ ] v1.0 release on PyPI
- [ ] v1.1 — hand-wraps for popular per-platform scrapers (community-driven)
- [ ] v1.2 — hosted HTTP/SSE transport
- [ ] v2.0 — caching layer for read-only ops + audit log for writes

## Contributing

Issues and PRs welcome. Please open a discussion before sinking time into a large change so we can align on shape.

If you want a tool that's missing because BD doesn't ship a public OpenAPI spec for it, file an issue with the endpoint URL and a sample `curl` — we can hand-wrap it under the appropriate group.

## Disclaimer

This is an **unofficial** community wrapper. Not affiliated with or endorsed by Bright Data. Built to fill a gap — the official MCP focuses on scraping; this one covers everything else.

Bright Data is a trademark of [Bright Data Ltd.](https://brightdata.com/) Use a valid Bright Data API token from your account settings.

## License

MIT — see [`LICENSE`](./LICENSE).
