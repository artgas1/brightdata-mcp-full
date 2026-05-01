# brightdata-mcp-full

> Comprehensive Python MCP server wrapping **100% of Bright Data's REST API** — 350+ tools across 16 product groups, auto-generated from OpenAPI specs.

[![status](https://img.shields.io/badge/status-spec--draft-orange)](./SPEC.md)
[![license](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![python](https://img.shields.io/badge/python-3.13+-blue)](#)

## Why this exists

[Bright Data's official MCP server](https://github.com/brightdata/brightdata-mcp) is excellent — 60+ tools for **scraping and web access**. But Bright Data's REST API is much larger: **350+ endpoints** including account management, proxy zones, IPs, billing, statistics, the LPM proxy manager, deep lookup, archive API, scraping shield, and more.

**`brightdata-mcp-full` complements the official MCP** by exposing everything else as a standalone, group-organized MCP server. Run them side by side:

```jsonc
// .mcp.json
{
  "mcpServers": {
    "brightdata":      { "url": "https://mcp.brightdata.com/mcp?token=..." },  // official: scraping
    "brightdata-full": { "command": "uv", "args": ["run", "..."] }              // this: everything else
  }
}
```

## Status

**In design phase.** SPEC under review. Implementation begins after spec is approved.

See [`SPEC.md`](./SPEC.md) for full design and roadmap.

## Tool groups (planned)

| Group | Tools | Examples |
|---|---:|---|
| `account_management` | 44 | balance, zones, IPs, stats, allowlist/denylist, billing |
| `proxy_manager` | 36 | LPM (Local Proxy Manager) — ports, users, IP bans |
| `scrapers` | 94 | Per-platform: Amazon, LinkedIn, Instagram, TikTok, Reddit, ... |
| `serp` | 68 | SERP API variants (Google, Bing, Yandex, DuckDuckGo, ...) |
| `marketplace_dataset` | 15 | Datasets, snapshots, S3/Azure delivery |
| `scraper_studio` | 14 | Custom scrapers via IDE |
| `rest_api` | 12 | Generic auth + utility |
| `proxy` | 12 | Connection settings |
| `deep_lookup` | 11 | Search + extract structured records |
| `archive` | 6 | Web archive snapshots |
| `scraping_shield` | 4 | Anti-scraping (defensive) |
| `browser_api` | 3 | Browser sessions list/get |
| `unlocker_rest` | 3 | Unlocker REST variants |
| `video_downloader` | 1 | Video download |
| `misc` | ~10 | Single endpoints |
| **Total** | **~350** | |

## Design highlights

- **Auto-generated from 31 OpenAPI specs** — `python scripts/regenerate.py` to update tools when BD's API changes
- **Group-based runtime selection** via `GROUPS=` env var (default: `account_management`) — keeps Claude's context lean
- **Write-gate via `BD_ENABLE_WRITES=true`** — read-only by default for safety; explicit opt-in for ops that create/delete/modify resources
- **Zero magic** — every tool is plain Python with typed Pydantic models, easy to read/audit
- **Stdio MCP** in v1, hosted HTTP/SSE planned for v2

## Planned setup (after v1 release)

```bash
uv add brightdata-mcp-full   # or pip install brightdata-mcp-full
export BRIGHT_DATA_API_TOKEN=your_token
uv run brightdata-mcp-full   # stdio MCP server
```

```jsonc
// Claude Desktop / Cursor / Claude Code config
{
  "mcpServers": {
    "brightdata-full": {
      "command": "uv",
      "args": ["run", "brightdata-mcp-full"],
      "env": {
        "BRIGHT_DATA_API_TOKEN": "your-token-here",
        "GROUPS": "account_management,deep_lookup",
        "BD_ENABLE_WRITES": "false"
      }
    }
  }
}
```

## Roadmap

- [ ] Spec review + approval (current)
- [ ] v1.0: Scaffolding + auto-generated 350 tools + tests + docs
- [ ] v1.1: Hosted HTTP/SSE transport
- [ ] v1.2: Caching layer (read-only ops)
- [ ] v2.0: Audit log for write operations

## Contributing

Spec-stage feedback is most welcome — open an issue or discussion. Code contributions accepted after v1.0 lands.

## Disclaimer

This is an **unofficial** community wrapper. Not affiliated with or endorsed by Bright Data. Built to fill a gap — the official MCP focuses on scraping; this one covers everything else.

Bright Data is a trademark of [Bright Data Ltd.](https://brightdata.com/) Use a valid Bright Data API token from your account settings.

## License

MIT — see [`LICENSE`](./LICENSE).
