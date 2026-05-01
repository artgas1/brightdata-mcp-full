---
title: "SPEC: brightdata-mcp-full — comprehensive 350-tool MCP server"
type: "spec"
status: "ready-for-dev"
linear_issue: "INFRA-160"
owner: "@artgas1"
last_updated: "2026-05-01"
license: "MIT"
tags: ["mcp", "brightdata", "auto-generated", "multi-agent"]
---

# brightdata-mcp-full — comprehensive 350-tool MCP server

> **Tracking:** [INFRA-160](https://linear.app/neirosova/issue/INFRA-160) (private, NeiroOwl team). Public PRs and discussions welcome.

## Проблема

Bright Data official MCP server (`@brightdata/mcp`, hosted at `mcp.brightdata.com`) покрывает только scraping и web-access — ~65 tools в Pro mode (`search_engine`, `scrape_as_markdown`, `scraping_browser_*`, `web_data_*`).

**Не покрыто officially: ~285 endpoints** из 350+ задокументированных в [`docs.brightdata.com/api-reference`](https://docs.brightdata.com/api-reference/):

- **44 account-management** — zones, IPs, balance, statistics, allowlist/denylist, billing
- **36 proxy-manager** — self-hosted LPM tool (ports, users, IP bans)
- **15 marketplace-dataset** — datasets, snapshots, S3/Azure delivery
- **14 scraper-studio** — custom scrapers via IDE
- **11 deep-lookup** — search+extract structured records (новый API)
- **6 archive-api** — web archive snapshots
- **+~159** прочие (serp variants, scrapers per-platform, scraping-shield, browser-sessions, etc.)

**Для NeiroOwl это блокер для:**

1. **Account management через Claude** — мы платим за BD, но balance check / zone management / IP allocation требует переключения в dashboard
2. **Future agentic workflows** — agent не может сам «купить ещё IPs если нужно» или «проверить usage и алертануть» — нужна account-management через MCP
3. **Comprehensive coverage** — community сейчас НЕ имеет full-coverage MCP для BD (проверено grep'ом ~80 GitHub repos 2026-05-01)

**Подтверждающие данные:**

- BD: $300M ARR, 20K+ business clients, 14 of 20 top LLM labs ([CTech Nov 2025](https://www.calcalistech.com/ctechnews/article/sjeyg2ezwe))
- Official MCP repo (`brightdata/brightdata-mcp`): 2.3K⭐, 60+ tools, scraping-only
- Community gap: ни одного MCP покрывающего account management (forks: sphilius, makaronz, cliztech, trizist — все scraping clones; collynce/brightdata-mcp-python — Python rewrite scraping; botlify-net/bright-data-api — TS lib без MCP)
- BD выложил `https://docs.brightdata.com/llms.txt` со списком 350 endpoints + 31 OpenAPI spec → готовая база для code-gen

## Решение

**`brightdata-mcp-full`** — comprehensive Python MCP server, **auto-generated из 31 OpenAPI spec'а Bright Data**.

**Ключевая идея:** одним PR покрываем 100% API surface через генератор, а не руками 350 раз. При обновлениях BD API — `python scripts/regenerate.py` → tools обновлены.

**Архитектура:**
- FastMCP-based, stdio transport (HTTP/SSE — v2)
- Group-based runtime loading через `GROUPS=` env var (как у official BD MCP)
- Read-only by default, write ops под `BD_ENABLE_WRITES=true` flag
- Auth: тот же `BRIGHT_DATA_API_TOKEN` что и для official MCP — переиспользуем
- Open source MIT — первый full-coverage MCP для BD в community

**Complementary к official:** не дублируем — наш MCP подключается **рядом** с официальным. Пользователь видит:
- `brightdata` (official) — для scraping/AI workflows
- `brightdata-full` (наш) — для account management + всего что не в официале

## Scope

### В scope

- **350+ MCP tools** покрывающих все 16 product groups BD API:
  - `account_management` (44 tools)
  - `proxy_manager` (36)
  - `scrapers` (94 — per-platform scrapers wrappers)
  - `serp` (68 — engine variants)
  - `marketplace_dataset` (15)
  - `scraper_studio` (14)
  - `rest_api` (12 — generic auth/proxy)
  - `proxy` (12 — connection settings)
  - `deep_lookup` (11)
  - `archive` (6)
  - `scraping_shield` (4)
  - `browser_api` (3 — sessions list/get)
  - `unlocker_rest` (3)
  - `video_downloader` (1)
  - `misc` (~10 single endpoints)
- **Code generator pipeline**: OpenAPI YAML → Pydantic models → FastMCP tools
- **Group-based runtime selection** через `GROUPS=` env var (default: `account_management`)
- **Write operations gated** через `BD_ENABLE_WRITES=true` (safety)
- **Auth wrapper** с retry, exponential backoff, structured errors
- **Unit tests** (mocked HTTP responses) + **integration tests** (live BD API smoke на free tier)
- **README** + per-group documentation
- **Open source MIT** license с самого начала
- **Регенерация script** для обновления при API changes BD

### НЕ в scope (non-goals)

- **Замена** official BD MCP — наш сервер complementary, оба подключаются параллельно в `.mcp.json`
- **Custom proxy connection / network layer** — мы wrapper над REST API, network handling остаётся у BD
- **Web UI** для управления — только CLI/MCP интерфейс
- **Hosted endpoint** (HTTP/SSE) — только stdio в v1, hosted в v2 если есть demand
- **Caching layer** — простой HTTP, без LRU/TTL в v1
- **Custom auth flow** (OAuth/SSO) — только bearer token API
- **CI/CD pipeline** — manual testing для v1, GitHub Actions в v2
- **NPM publication** — Python only в v1, JS port — отдельный проект если нужен
- **`web_data_*` tools / browser automation** — это уже в official MCP, не дублируем

## Acceptance Criteria

- **GIVEN** Claude Code config с подключённым `brightdata-mcp-full` и `BRIGHT_DATA_API_TOKEN` env  
  **WHEN** Claude Code запускается  
  **THEN** `/mcp` показывает `brightdata-mcp-full` connected, активные tools зависят от `GROUPS=`

- **GIVEN** `GROUPS=account_management` (default)  
  **WHEN** Claude Code загружает MCP  
  **THEN** активны 44 account tools, остальные ~310 не зарегистрированы (экономит context)

- **GIVEN** `GROUPS=account_management,proxy_manager,deep_lookup`  
  **WHEN** Claude Code загружает MCP  
  **THEN** активны 91 tool из 3 групп

- **GIVEN** `BD_ENABLE_WRITES=true` + `GROUPS=account_management`  
  **WHEN** агент вызывает `bd_zone_create` через MCP  
  **THEN** zone создаётся в реальном BD аккаунте через `POST /zone`

- **GIVEN** `BD_ENABLE_WRITES=false` (default)  
  **WHEN** агент вызывает write tool  
  **THEN** возвращается structured error: `{ "error": "Write operations disabled. Set BD_ENABLE_WRITES=true to enable." }`

- **GIVEN** обновление BD API (новый endpoint в OpenAPI spec)  
  **WHEN** разработчик запускает `python scripts/regenerate.py`  
  **THEN** новый tool auto-generated в соответствующую группу, существующие сохранены

- **GIVEN** integration test suite  
  **WHEN** запускается `pytest tests/integration -k account_management`  
  **THEN** ≥80% account tools проходят smoke test против live BD API

## Technical Approach

### Stack

| Component | Choice | Why |
|---|---|---|
| Language | Python 3.13 | Совместимость с monorepo, BD имеет Python SDK |
| Package manager | uv | Текущий стандарт для NeiroOwl Python |
| MCP framework | [FastMCP](https://github.com/jlowin/fastmcp) 0.4+ | Самый зрелый Python MCP, type-safe decorators |
| HTTP client | httpx (async) | Поддержка retry, async, такой же как в backend/ |
| OpenAPI parsing | [openapi-pydantic](https://github.com/mike-oakley/openapi-pydantic) + custom emitter | Конверсия в типизированные Pydantic models |
| Pydantic models | [datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator) | Auto-генерация моделей из schemas |
| Testing | pytest + pytest-asyncio + responses + pytest-recording | Mock + record-replay для live tests |

### Project Layout

**Repo:** `github.com/artgas1/brightdata-mcp-full` (standalone, public, MIT) — личный repo Артёма для open-source. Не в `CheekyExplosion` org и не в monorepo `ai-prototype`.

```
brightdata-mcp-full/                 # standalone repo
├── pyproject.toml                   # uv project, deps, console script entry
├── README.md                        # main docs, quick start, GROUPS list
├── LICENSE                          # MIT
├── server.py                        # FastMCP entry, GROUPS= env loader
├── lib/
│   ├── __init__.py
│   ├── client.py                    # httpx wrapper: auth, retry, error
│   ├── codegen.py                   # OpenAPI → tools generator (used by scripts/regenerate.py)
│   ├── groups.py                    # GROUPS= parser, dynamic loader
│   ├── safety.py                    # write-gate enforcement
│   └── types/                       # auto-generated Pydantic models
│       ├── account_management.py
│       ├── proxy_manager.py
│       └── ...
├── tools/                           # auto-generated FastMCP tools, regen on demand
│   ├── account_management/
│   │   ├── __init__.py              # registers tools to mcp instance
│   │   ├── bd_account_get_balance.py
│   │   ├── bd_zone_list.py
│   │   ├── ...                       # 44 files
│   │   └── README.md                # group-specific docs
│   ├── proxy_manager/                # 36 files
│   ├── scrapers/                     # 94 files
│   ├── serp/                         # 68 files
│   ├── ... (16 groups total)
├── tests/
│   ├── unit/                        # Mock HTTP, fast
│   │   ├── test_client.py
│   │   ├── test_groups.py
│   │   ├── test_safety.py
│   │   └── test_tools_*.py
│   └── integration/                 # Live BD API, slow
│       ├── conftest.py
│       └── test_*_integration.py
├── scripts/
│   ├── regenerate.py                # Fetch OpenAPI specs + run codegen
│   └── verify_coverage.py           # Sanity check tool count vs BD docs
└── docs/
    ├── groups.md                    # Detail per group
    ├── auth.md                      # Auth flow
    └── examples.md                  # Usage examples
```

### Code Generator Pipeline (`lib/codegen.py`)

```python
# Pseudocode flow:
def regenerate_all():
    for spec_url in fetch_openapi_specs_from_llms_txt():
        spec = fetch_and_parse(spec_url)
        group = derive_group_from_url(spec_url)  # account_management, etc.
        
        for operation in spec.operations:
            tool_module = generate_tool_module(operation, group)
            write_to(f"tools/{group}/{tool_module.name}.py", tool_module)
        
        write_init_file(group)
    
    update_root_init()
```

Каждый сгенерированный tool выглядит так:

```python
# tools/account_management/bd_account_get_balance.py (auto-generated)
from typing import Annotated
from lib.client import bd_request
from lib.safety import requires_write_enabled
from lib.types.account_management import GetBalanceResponse

GROUP = "account_management"
WRITES = False  # read-only

async def bd_account_get_balance() -> GetBalanceResponse:
    """
    Get the total balance through API.
    
    Returns the current account balance and pending costs (next billing).
    
    From: GET /api/customer/balance
    Docs: https://docs.brightdata.com/api-reference/account-management-api/Get_total_balance_through_API
    """
    response = await bd_request("GET", "/api/customer/balance")
    return GetBalanceResponse.model_validate(response)
```

`server.py` собирает их по группам:

```python
# server.py
from fastmcp import FastMCP
from lib.groups import load_groups_from_env

mcp = FastMCP("brightdata-mcp-full")

groups_to_load = load_groups_from_env()  # ["account_management"] by default
for group in groups_to_load:
    register_tools_for_group(mcp, group)

if __name__ == "__main__":
    mcp.run()
```

### Multi-agent Implementation Plan

**Round 1 — A1 architect (1 agent, sequential, ~30 min):**
- `uv init` project, deps, pyproject.toml
- `server.py` with `GROUPS=` loader
- `lib/client.py` (auth, retry exponential backoff, error wrapping)
- `lib/safety.py` (write gate)
- `lib/codegen.py` skeleton (interfaces, no implementation yet)
- 3 hand-written smoke tools для bootstrap (`bd_account_get_balance`, `bd_zone_list`, `bd_account_get_status`)
- Unit tests for `lib/`

**Round 2 — A2 codegen-engineer (1 agent, sequential after A1, ~1 hour):**
- Fetch all 31 OpenAPI specs from `docs.brightdata.com/llms.txt`
- Cache в `specs/openapi/` (gitignored для регенерации)
- Implement `lib/codegen.py`:
  - Parse OpenAPI YAML/JSON via `openapi-pydantic`
  - Generate Pydantic models per schema → `lib/types/{group}.py`
  - Generate FastMCP tool function per operation → `tools/{group}/{tool}.py`
  - Generate `__init__.py` per group with registration logic
- Run generator → 350 tools generated
- Smoke-test первые 3 tool из каждой группы

**Round 3 — A3-A9 parallel (7 agents в одном message, ~4-6 часов):**

Каждый агент получает single message с context:
- Группу за которую отвечает
- Pre-generated tools в `tools/{group}/`
- Задание: integration smoke test, доработка descriptions если OpenAPI скудно описаны, edge cases

| Agent | Группа | Tools | Live tests |
|---|---|---:|---|
| **A3** | account_management | 44 | All read-only tools против live BD account |
| **A4** | proxy_manager | 36 | Skip live tests если LPM не setup'нут — only mocked |
| **A5** | scrapers | 94 | Sample 5 popular (Amazon, LinkedIn, IG, TikTok, Reddit) |
| **A6** | serp | 68 | Sample 3 engines (Google/Bing/Yandex) |
| **A7** | deep_lookup + archive + browser_api | 20 | Live tests где возможно |
| **A8** | misc (rest_api + proxy + studio + shield + video + unlocker REST) | ~50 | Mocked + 3-5 live samples |
| **A9** | tests harness + CI placeholder | — | Pytest infrastructure, fixtures, conftest |

**Round 4 — A10 integration tester (1 agent, sequential, ~30 min):**
- Run full integration suite против live BD account
- Verify GROUPS= filtering works correctly (3 различных configs)
- Verify BD_ENABLE_WRITES=false blocks all writes correctly
- Coverage report

**Round 5 — A11 docs writer (1 agent, ~30 min):**
- README с install + quick start + всеми GROUPS
- `docs/groups.md` со списком всех 350 tools
- `docs/auth.md` с auth flow
- `docs/examples.md` с 5-10 usage scenarios
- LICENSE (MIT)

**Total wall-clock: 1.5-2 days** (Rounds 1-2 sequential ~1.5 часа, Round 3 параллельно ~4-6 часов, Rounds 4-5 ~1 час).

### Sub-agent Brief Template

Для каждого Round 3 agent брифинг такой:

```
You are agent A{N} working on `brightdata-mcp-full` MCP server.

Your scope: group `{group_name}` containing {count} auto-generated MCP tools at `tools/{group_name}/`.

Background: This is a comprehensive Python MCP server wrapping Bright Data's full REST API
(350+ endpoints, 31 OpenAPI specs). Tools were auto-generated by codegen pipeline. Your job
is QA and polish.

Context (read these first):
- SPEC: ai-prototype-bd-mcp-full/specs/SPEC-0007-brightdata-mcp-full.md
- Generator: ai-prototype-bd-mcp-full/lib/codegen.py
- Pre-generated tools: ai-prototype-bd-mcp-full/tools/{group_name}/

Tasks:
1. Verify each tool's docstring is sufficient (BD descriptions can be terse)
2. Run integration smoke test for read-only tools against `BRIGHT_DATA_API_TOKEN`
3. Mark write operations clearly with confirmation prompt в description
4. Check error handling — tools should return structured errors, not raise
5. Add unit test for at least 3 representative tools

Constraints:
- Don't change auto-generated structure (must survive regenerate)
- Use override hooks in `lib/codegen.py` if описание недостаточно
- Report any BD API endpoints that don't work as documented

Report when done: tool count tested, issues found, write tools tagged correctly.
Reference: per `.claude/rules/sub-agent-defaults.md`, отчитайся под 200 слов.
```

### Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| OpenAPI specs incomplete на BD docs | Some tools missing | Fallback на manual wrap по zendesk docs (~10 endpoints) |
| Tool selection accuracy с 350 tools | Claude путается выбирая правильный | `GROUPS=` env var дефолт `account_management` (44 tools) |
| BD rate limits при mass-test | Codegen или integration tests блокируются | Rate limiter в `lib/client.py` (max 10 req/sec), pytest-recording |
| BD API breaking changes | Tools перестают работать | `regenerate.py` команда, pinned versions в pyproject |
| Maintenance burden 350 tools | Долгосрочный overhead | Auto-generated → minimal manual code; open-source community contrib |
| Write operations случайно вызваны | Создание/удаление zones | `BD_ENABLE_WRITES=false` default + structured error |
| Free tier rate limits during dev | Codegen блокирует тестирование | Mocked unit tests первичны, live tests sparse |

### Open Questions

1. ~~**Где репо в итоге живёт?**~~ **Resolved 2026-05-01:** standalone `github.com/artgas1/brightdata-mcp-full`, public + MIT с самого начала. Не в `CheekyExplosion` org, не в `ai-prototype` monorepo.

2. **CI/CD setup?**
   - Default: пропускаем в v1 (manual test перед releases)
   - GitHub Actions в v2 если active maintenance

3. **Hosted endpoint (HTTP/SSE)?**
   - Default: только stdio в v1
   - HTTP/SSE если будет demand из community

4. **`web_data_*` tools — wrap для self-sufficient setup?**
   - Default: НЕ дублируем (рекомендуем official MCP параллельно)
   - Если community просит — отдельный `--include-overlap` flag в v2

5. **Audit log для write operations?**
   - Default: только лог через standard logging
   - Persistent audit (БД/файл) — v2 опция

6. **Scraper Studio specific endpoints (14 tools)** — некоторые могут быть paid-only
   - Mitigation: graceful fallback когда tool возвращает 403

7. **Linear branch naming** — `aggasparyan/infra-159-spec-bd-mcp-full` или `spec/bd-mcp-full`?
   - Текущее: `spec/bd-mcp-full` (краткое для repo conventions)

## Implementation Phases (Linear issues)

Phase 3 в существующем Linear project «Миграция proxy: SpaceProxy → Bright Data»:

1. **INFRA-160** SPEC-0007 brightdata-mcp-full draft + ready-for-dev (this issue)
2. **INFRA-161** A1 scaffolding (uv project, FastMCP, lib/client.py, 3 smoke tools)
3. **INFRA-162** A2 codegen pipeline (OpenAPI → 350 tools)
4. **INFRA-163** Round 3 — 7 parallel agents QA all groups
5. **INFRA-164** A10 integration testing
6. **INFRA-165** A11 docs + LICENSE + README
7. **INFRA-166** Register `brightdata-mcp-full` в `.mcp.json` + verify в Claude Code

Все assignee — Claude (исполняется автономно), human review на каждом merge.

## References

- [Bright Data API Reference index](https://docs.brightdata.com/api-reference/)
- [`docs.brightdata.com/llms.txt`](https://docs.brightdata.com/llms.txt) — 770-line index с 350 endpoints + 31 OpenAPI specs
- [Bright Data Account Management API](https://docs.brightdata.com/api-reference/account-management-api/)
- [Official BD MCP](https://github.com/brightdata/brightdata-mcp) — что НЕ дублируем
- [Bright Data Python SDK](https://github.com/brightdata/sdk-python) — for reference patterns
- [FastMCP framework](https://github.com/jlowin/fastmcp)
- [datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator)
- [`.claude/rules/sub-agent-defaults.md`](https://github.com/CheekyExplosion/NeiroOwl-claude/blob/main/rules/sub-agent-defaults.md) — multi-agent execution patterns
- [`.claude/rules/ai-content-in-ai-repo.md`](https://github.com/CheekyExplosion/NeiroOwl-claude/blob/main/rules/ai-content-in-ai-repo.md) — почему spec живёт в `ai-prototype/`
- Linear Project: [Миграция proxy: SpaceProxy → Bright Data](https://linear.app/neirosova/project/migraciya-proxy-spaceproxy-bright-data-087da7e9b0a9)
- [Bright Data $300M ARR — CTech Nov 2025](https://www.calcalistech.com/ctechnews/article/sjeyg2ezwe)
- Discussion thread: chat session 2026-05-01 (proxy migration research)
