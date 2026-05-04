# Contributing

Thanks for your interest. This project is small and pragmatic — issues, PRs,
and bug reports are welcome.

## Development setup

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/artgas1/brightdata-mcp-full.git
cd brightdata-mcp-full
uv sync --all-extras
```

## Running locally

```bash
export BRIGHT_DATA_API_TOKEN="your-token"
export GROUPS="account_management"        # or "all", or any comma-separated subset
export BD_ENABLE_WRITES="false"           # default — read-only

uv run python server.py
```

The server speaks MCP over stdio. Wire it into a Claude Code / IDE
`.mcp.json` (see `README.md` for an example).

## Tests

```bash
# Unit tests — fast, no network, no token needed
uv run pytest tests/unit -v

# Integration tests — require BRIGHT_DATA_API_TOKEN and live BD API
uv run pytest tests/integration -v
```

CI runs lint + typecheck + unit tests on every PR. Integration tests run
locally only.

## Lint / format / typecheck

```bash
uv run ruff check .          # lint
uv run ruff format .         # format
uv run pyright lib/ server.py  # typecheck
```

## Adding tools

149 tools are auto-generated from OpenAPI specs in `specs/`. To add or refresh:

1. Drop a new OpenAPI spec into `specs/<group>/<name>.yaml`.
2. Run `python scripts/regenerate.py`.
3. Generated tools land in `tools/<group>/`. Smoke-tools (marked with
   `# SMOKE-TOOL: hand-written, do not regenerate`) are preserved.

To replace an auto-generated tool with a hand-written one (for richer
docstrings or non-trivial parameter handling), add the smoke marker and edit
the file — the regenerator will skip it.

## Commit style

Conventional Commits. Most commonly:

- `feat: …` — user-visible new tool / feature
- `fix: …` — bugfix
- `chore: …` — internal hygiene (deps, CI, codegen)
- `docs: …` — documentation only

## Release

Maintainer: tag `vX.Y.Z` on `main`. The `publish.yml` workflow builds and
publishes to PyPI via Trusted Publisher (no API tokens in repo secrets).

## License

MIT. By contributing, you agree your contributions are licensed under MIT.
