# Usage examples

Seven scenarios for `brightdata-mcp-full`. All tool names are real — verify in [`docs/groups.md`](./groups.md) or `tools/<group>/`.

Set `BRIGHT_DATA_API_TOKEN` first (see [`auth.md`](./auth.md)). Examples assume Claude Code as the MCP client; the same calls work from any MCP client (Claude Desktop, Cursor, custom).

---

## 1. Check account zones

> "List all zones on my Bright Data account."

Required scope: `account read`. No write gate.

Tools used:
- `bd_account_management_list_zone_get_all_zones()` — returns every zone, active or not
- `bd_account_management_list_zone_get_active_zones()` — returns only zones currently enabled

```
Use bd_account_management_list_zone_get_all_zones to list every zone on this account.
For each zone, also call bd_account_management_get_zone(zone="<name>") to fetch its
configuration (type, country, password ID).
```

Default `GROUPS=account_management` covers this — no extra config needed.

---

## 2. Get account status

> "Is my Bright Data account active and able to make requests?"

Required scope: minimal — works on free tier. Read-only.

Tools used:
- `bd_account_get_status()` — `{status, customer, can_make_requests, auth_fail_reason, ip}`

```
Call bd_account_get_status and report whether can_make_requests is true.
If false, surface the auth_fail_reason field so the user knows why.
```

This is the cheapest end-to-end smoke test — works without any zones provisioned.

---

## 3. Run a deep lookup

> "Find me the LinkedIn profile, email, and current company for the founder of Bright Data."

Required scope: `deep lookup`. Trigger is a write op (charged per query) — set `BD_ENABLE_WRITES=true`.

Tools used:
- `bd_deep_lookup_create_preview()` — cheap dry-run that previews what the trigger would return
- `bd_deep_lookup_create_trigger()` — actually executes the query (billable)
- `bd_deep_lookup_get_request_by_id_status(id="<request_id>")` — poll status
- `bd_deep_lookup_get_request_by_id(id="<request_id>")` — fetch the result

```
Step 1: bd_deep_lookup_create_preview(body={"query": "Founder of Bright Data — LinkedIn URL, current email, current company"})
Step 2: If the preview looks right, bd_deep_lookup_create_trigger(body={...same...})
Step 3: Poll bd_deep_lookup_get_request_by_id_status until it returns "completed"
Step 4: bd_deep_lookup_get_request_by_id to get the structured result
```

Add `GROUPS=account_management,deep_lookup` to your MCP config to surface these tools.

---

## 4. List BD marketplace datasets

> "What pre-collected datasets does Bright Data offer? I want to scrape LinkedIn profiles in bulk."

Required scope: `marketplace dataset` (read). No write gate.

Tools used:
- `bd_marketplace_dataset_list_datasets()` — catalog of all datasets BD ships
- `bd_marketplace_dataset_list_datasets_views()` — pre-built views (filtered slices)
- `bd_marketplace_dataset_get_datasets_snapshots_by_id(id="<dataset_id>")` — inspect a snapshot's metadata

```
List all datasets via bd_marketplace_dataset_list_datasets.
Filter the JSON result for items where the name contains "linkedin" or "profile".
For each match, show price-per-record and last-update date.
```

Add `GROUPS=account_management,marketplace_dataset` to surface these.

---

## 5. Allow IPs to a zone (write op)

> "Add `203.0.113.42` to the whitelist of zone `mcp_unlocker`."

Required scope: `zones write`. **Requires `BD_ENABLE_WRITES=true`** — otherwise tool returns `{"error": "Write operations disabled. Set BD_ENABLE_WRITES=true to enable.", "status_code": 403}`.

Tools used:
- `bd_account_management_get_zone_whitelist(zone="mcp_unlocker")` — see current allowlist
- `bd_account_management_create_zone_whitelist(body={"zone": "mcp_unlocker", "ip": "203.0.113.42"})` — add the entry

```
Step 1: bd_account_management_get_zone_whitelist(zone="mcp_unlocker") — confirm IP isn't already there
Step 2: bd_account_management_create_zone_whitelist(body={"zone": "mcp_unlocker", "ip": "203.0.113.42"})
Step 3: Re-fetch the whitelist to verify
```

The write gate is intentional friction — these ops change billable resources. Set the flag explicitly when you're sure.

---

## 6. Search the web archive

> "Find archived snapshots of `nytimes.com` from 2020."

Required scope: `archive` (write — search submission is async). Requires `BD_ENABLE_WRITES=true`.

Tools used:
- `bd_archive_create_webarchive_search(body={"url": "nytimes.com", "from_date": "2020-01-01", "to_date": "2020-12-31"})` — submit search
- `bd_archive_get_webarchive_search_by_search_id(search_id="<id>")` — fetch results

```
Step 1: bd_archive_create_webarchive_search(body={"url": "nytimes.com", "from_date": "2020-01-01", "to_date": "2020-12-31"})
Step 2: Take the search_id from the response, poll bd_archive_get_webarchive_search_by_search_id
Step 3: For interesting snapshots, optionally trigger bd_archive_create_webarchive_dump to get the full content
```

`GROUPS=archive` (or `account_management,archive`).

---

## 7. Multi-group setup for an agent

A research agent that needs zones, datasets, deep lookup, and archive — but not the long tail of marketplace + scraper studio tools (keeps Claude's tool selection fast):

```jsonc
// Claude Code .mcp.json
{
  "mcpServers": {
    "brightdata-full": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/brightdata-mcp-full", "python", "server.py"],
      "env": {
        "BRIGHT_DATA_API_TOKEN": "eb4b8059-...",
        "GROUPS": "account_management,deep_lookup,archive",
        "BD_ENABLE_WRITES": "true"
      }
    }
  }
}
```

This loads exactly **85 tools** (70 + 9 + 6) instead of all 149 — Claude's tool-picker stays sharp, and unrelated `marketplace_dataset` / `scrapers` paths aren't candidates for fuzzy-match mistakes.

To check what got loaded, run `/mcp` in Claude Code and look at the `brightdata-full` section.
