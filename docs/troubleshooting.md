# Troubleshooting

Quick lookups for the errors you'll actually hit. Each entry: symptom → root cause → fix.

## Tool returned `403 Your API key lacks the required permissions`

**Cause:** Your `BRIGHT_DATA_API_TOKEN` is valid but doesn't have the scope this endpoint requires. The path itself is correct.

**Fix:** Open [BD dashboard → Settings → API Tokens](https://brightdata.com/cp/setting/users), edit the token, and tick the missing permission (e.g. `customer balance` for `bd_account_get_balance`, `zones write` for any `bd_account_management_create_zone_*`). See [`auth.md`](./auth.md) for the scope→endpoint matrix.

If you can't change the token, mint a separate token with the required scope and switch `BRIGHT_DATA_API_TOKEN` for that workflow.

## Tool returned `404 Not Found`

**Cause:** Either (a) the endpoint was deprecated/moved by Bright Data after our codegen run, or (b) you're calling a path-parametrised endpoint with an ID that doesn't exist on your account (e.g. `bd_marketplace_dataset_get_datasets_snapshots_by_id(id="bogus")`).

**Fix:**
1. Check the live BD docs at the URL in the tool's docstring (`Docs:` line) — confirm the endpoint still exists.
2. If the endpoint is gone, regenerate: `uv run python scripts/regenerate.py` (pulls fresh OpenAPI specs).
3. If the endpoint is fine but ID is wrong, list the right IDs first (e.g. `bd_marketplace_dataset_list_datasets_snapshots`) and feed the result back in.

## `Connection timeout` / `httpx.ConnectError`

**Cause:** BD API is unreachable from your network — either local connectivity, BD outage, or proxy/firewall blocking `api.brightdata.com`.

**Fix:**
1. Check [BD's status page](https://status.brightdata.com/) for ongoing incidents.
2. From the same machine: `curl -v https://api.brightdata.com/status` — should return JSON.
3. Behind a corporate proxy? Set `HTTPS_PROXY=http://your-proxy:port` before launching the MCP.
4. Persistent timeouts only on writes? Some BD write endpoints take 30+ seconds — bump the client timeout in `lib/client.py` if you've customised it.

## Tool returned `Write operations disabled. Set BD_ENABLE_WRITES=true to enable.`

**Cause:** You called a `WRITES = True` tool (anything that creates, updates, or deletes BD resources) without explicitly opting in.

**Fix:** Set `BD_ENABLE_WRITES=true` in your env or MCP config and restart the server. This gate is intentional — write ops touch billable resources, so opt-in is required per session.

```jsonc
// Claude Code config
"env": {
  "BRIGHT_DATA_API_TOKEN": "...",
  "BD_ENABLE_WRITES": "true"   // ← add this line
}
```

To see which tools are write ops, check `WRITES = True` in `tools/<group>/bd_*.py` or filter [`groups.md`](./groups.md) for the `write` flag.

## Tool not found in `/mcp`

**Cause:** The tool's group isn't in your `GROUPS=` env var. Default is `GROUPS=account_management` only — everything else is excluded to keep Claude's context lean.

**Fix:** Add the group(s) you need to your MCP config:

```jsonc
"env": {
  "GROUPS": "account_management,deep_lookup,archive,marketplace_dataset"
}
```

Restart the MCP server (or Claude Code itself) so the launcher rereads env vars. Run `/mcp` to confirm — `brightdata-full` should now show the expanded tool list.

To load every group at once: `GROUPS=*`. Useful for exploration; not recommended for daily use (149 tools dilutes Claude's tool selection).

## Tool returned cryptic `{"error": "...", "status_code": 400}`

**Cause:** Bright Data validated the request body and rejected it. The `details` field of the error usually contains BD's specific complaint.

**Fix:** Check the tool's docstring for the `From: <METHOD> <path>` line, then look up the corresponding `Docs:` URL — BD's API reference shows the expected request schema. Compare your `body=` against the schema and fix the offending field.

The auto-generated tools don't validate request bodies on the client side (BD's OpenAPI specs are too loose for strict client validation), so malformed payloads always round-trip to BD before failing.

## MCP server starts but `/mcp` shows zero tools from `brightdata-full`

**Cause:** Either the server crashed silently on startup, or `GROUPS=` doesn't match any registered group.

**Fix:**
1. Run the server manually: `uv run python server.py` from the repo root and watch stderr for tracebacks.
2. Confirm `GROUPS` value matches an existing directory in `tools/` (case-sensitive: `account_management`, not `Account_Management`).
3. Confirm `BRIGHT_DATA_API_TOKEN` is set — server may refuse to start without it.
