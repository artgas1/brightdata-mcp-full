# Authentication

`brightdata-mcp-full` authenticates against Bright Data's REST API using a single bearer token (`BRIGHT_DATA_API_TOKEN`). Same token format as the official BD MCP — if you already have one set up, reuse it.

## Where to get the token

1. Sign in to the [Bright Data dashboard](https://brightdata.com/cp).
2. Navigate to **Settings → API Tokens** (`brightdata.com/cp/setting/users`).
3. Click **Add Token**. Pick a name (e.g. `mcp-full`) and select the permissions you want (see next section).
4. Copy the token. BD shows it only once — store it in a secrets manager or your `.env`.

## Token permissions matter

BD tokens are scoped. The same endpoint can return `200` for one token and `403 "Your API key lacks the required permissions"` for another. Common scopes:

| Permission | Endpoints it unlocks |
|---|---|
| `account read` | `GET /status`, `GET /zone`, `GET /zone/get_active_zones`, ... |
| `customer balance` | `GET /customer/balance` |
| `zones write` | `POST /zone`, `POST /zone/ips`, `DELETE /zone`, ... |
| `marketplace dataset` | `bd_marketplace_dataset_*` (read + trigger) |
| `deep lookup` | `bd_deep_lookup_*` |

If a tool returns a structured `{"error": "...", "status_code": 403}` payload, the path is correct but the token lacks scope. Add the missing permission in the dashboard or mint a separate token for the workflow.

## Setting the token

### Via env var (preferred for production / hosted setups)

```bash
export BRIGHT_DATA_API_TOKEN=eb4b8059-...
uv run python server.py
```

### Via `.env` file (preferred for local dev)

Create `.env` in the project root (gitignored):

```
BRIGHT_DATA_API_TOKEN=eb4b8059-...
GROUPS=account_management,deep_lookup
BD_ENABLE_WRITES=false
```

`server.py` loads this automatically via `python-dotenv`.

### Via Claude Code / Claude Desktop config

```jsonc
{
  "mcpServers": {
    "brightdata-full": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/brightdata-mcp-full", "python", "server.py"],
      "env": {
        "BRIGHT_DATA_API_TOKEN": "eb4b8059-...",
        "GROUPS": "account_management,deep_lookup",
        "BD_ENABLE_WRITES": "false"
      }
    }
  }
}
```

## Verifying the token works

The cheapest end-to-end check is `GET /status` — it requires no zone setup and works on free-tier accounts:

```bash
curl -H "Authorization: Bearer $BRIGHT_DATA_API_TOKEN" https://api.brightdata.com/status
# → {"status":"active","customer":"hl_xxxxxxxx","can_make_requests":false,"auth_fail_reason":"zone_not_found","ip":"..."}
```

If you get JSON back (even with `can_make_requests: false`), auth is fine. The next step is to provision at least one zone in the dashboard so `can_make_requests` flips to `true`.

## What's out of scope for this MCP

The token described above is for **REST API** calls only. Bright Data's other access methods are not handled here:

- **Native proxy access** (`brd-customer-...`/`zone-...`/`password` over `brd.superproxy.io:33335`) — use BD's official proxy SDK or your HTTP client's proxy settings directly. The MCP wraps REST endpoints, not the proxy network.
- **Browser API WebSocket** — `wss://brd.superproxy.io:9222` is consumed by Playwright/Puppeteer; the MCP exposes the REST management endpoints (`bd_browser_api_*`) only.
- **OAuth / SSO** — BD doesn't ship OAuth for the API; bearer tokens are the only auth flow.

## Rotating tokens

Tokens don't expire by default but can be revoked from the dashboard. To rotate:

1. Mint a new token with the same scopes.
2. Update `BRIGHT_DATA_API_TOKEN` in your env / `.env` / MCP config.
3. Restart the MCP server (`pkill -f "python server.py"` and let your launcher relaunch).
4. Revoke the old token in the dashboard.
