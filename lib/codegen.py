"""Codegen pipeline — fetches BD's OpenAPI specs and emits FastMCP tools.

Produced by INFRA-162 (A2). Consumed by `scripts/regenerate.py`.

Design notes
------------

- The 31 specs listed in `https://docs.brightdata.com/llms.txt` include 16 unique
  English specs and 15 Chinese duplicates (`cn-*`). We skip the `cn-*` clones —
  they expose the same endpoints with translated descriptions and would just
  produce duplicate tools.
- Spec → group mapping is hand-authored (`SPEC_GROUP_MAP` below). It mirrors the
  group taxonomy fixed in `lib/groups.py` (KNOWN_GROUPS).
- We dedupe on `(method, path)` across specs that share a group — several specs
  reference the same endpoint (e.g. `POST /datasets/v3/trigger` is in
  `scraper-rest-api`, `crawl-rest-api`, and `dca-api`). The first spec to claim
  a path wins.
- For each operation we emit one Python module under `tools/<group>/<name>.py`.
- Tool names are derived deterministically from `(group, method, path)` so
  regeneration is idempotent — a given endpoint always lands in the same file.
- Request bodies and responses are kept as `dict[str, Any]` for now; rich
  Pydantic models would require deep `$ref` resolution and add fragile
  generation surface. Round 3 agents can refine per-tool if needed.
- Hand-written smoke tools (A1's three `tools/account_management/*.py` files)
  are preserved via the `# SMOKE-TOOL: hand-written` marker. Regen never
  overwrites a file containing that marker.
"""

from __future__ import annotations

import json
import keyword
import re
import textwrap
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .groups import KNOWN_GROUPS

# --------------------------------------------------------------------------- #
# Configuration                                                               #
# --------------------------------------------------------------------------- #

REPO_ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = REPO_ROOT / "specs" / "openapi"
TOOLS_DIR = REPO_ROOT / "tools"

LLMS_TXT_URL = "https://docs.brightdata.com/llms.txt"

SMOKE_MARKER = "# SMOKE-TOOL: hand-written, do not regenerate"

# Map each English spec stem to a group from KNOWN_GROUPS.
# `cn-*` stems are intentionally absent — they're skipped during fetch/parse.
SPEC_GROUP_MAP: dict[str, str] = {
    "openapi": "account_management",
    "openapi-reseller": "account_management",
    "proxy-manager": "proxy_manager",
    "dca-api": "marketplace_dataset",
    "datasets-rest-api": "marketplace_dataset",
    "scraper-rest-api": "scrapers",
    "crawl-rest-api": "scrapers",
    "web-scraper-ide-rest-api": "scraper_studio",
    "serp-rest-api": "serp",
    "proxy-rest-api": "proxy",
    "deep-lookup": "deep_lookup",
    "web-archive-api": "archive",
    "scraping-shield-rest-api": "scraping_shield",
    "browser-api": "browser_api",
    "unlocker-rest-api": "unlocker_rest",
    "video-downloader": "video_downloader",
    "async-api-reference": "misc",
    "filter-csv-json": "misc",
    "dca-custom-inputs": "misc",
}


# --------------------------------------------------------------------------- #
# IR                                                                          #
# --------------------------------------------------------------------------- #


@dataclass
class ToolDef:
    """Intermediate representation of one MCP tool, derived from one OpenAPI operation."""

    name: str
    """Snake_case tool function name, e.g. `bd_account_management_get_zone`."""

    group: str
    """Group identifier from KNOWN_GROUPS."""

    method: str
    """HTTP method (GET/POST/PUT/DELETE/PATCH)."""

    path: str
    """API path with `/` prefix and `{param}` placeholders preserved."""

    summary: str
    """One-line summary lifted from OpenAPI `summary` field (may be empty)."""

    description: str
    """Multi-line description from OpenAPI `description` field (may be empty)."""

    docs_url: str
    """Link to the BD docs page for this operation."""

    parameters: list[dict[str, Any]] = field(default_factory=list)
    """OpenAPI parameter definitions (path/query/header). Each: {name, in, required, schema}."""

    has_request_body: bool = False
    """True if the operation has a JSON request body."""

    is_write: bool = False
    """True if method is POST/PUT/PATCH/DELETE — wrapped in `@requires_write_enabled`."""

    spec_source: str = ""
    """Stem(s) of the spec file(s) this op came from (for traceability)."""


# --------------------------------------------------------------------------- #
# Public API                                                                  #
# --------------------------------------------------------------------------- #


def fetch_openapi_specs() -> dict[str, dict[str, Any]]:
    """Fetch all 31 OpenAPI specs from docs.brightdata.com and parse to dicts.

    Caches raw specs to `specs/openapi/<stem>.json` (gitignored) for offline regen.
    Returns mapping `{group_name: parsed_openapi_dict}`. When multiple specs map
    to the same group (e.g. `openapi` + `openapi-reseller` → `account_management`),
    the parsed specs are merged at the `paths` level — first spec wins on collision.

    Returns:
        Mapping of group identifier to a parsed OpenAPI 3.x document.
    """
    SPECS_DIR.mkdir(parents=True, exist_ok=True)

    spec_urls = _discover_spec_urls()

    parsed_by_stem: dict[str, dict[str, Any]] = {}
    for stem, url in spec_urls.items():
        if stem.startswith("cn-"):
            continue  # skip Chinese duplicates
        if stem not in SPEC_GROUP_MAP:
            continue  # unknown stem — skip silently
        cache = SPECS_DIR / f"{stem}.json"
        if not cache.exists():
            print(f"  [fetch] {stem} ← {url}")
            data = _http_get_bytes(url)
            cache.write_bytes(data)
        parsed_by_stem[stem] = json.loads(cache.read_text())

    # Merge specs that share a group.
    by_group: dict[str, dict[str, Any]] = {}
    for stem, spec in parsed_by_stem.items():
        group = SPEC_GROUP_MAP[stem]
        if group not in by_group:
            by_group[group] = {
                "openapi": spec.get("openapi", "3.0.0"),
                "info": spec.get("info", {}),
                "paths": {},
                "components": {"schemas": {}},
                "_sources": [stem],
            }
        else:
            by_group[group]["_sources"].append(stem)
        merged = by_group[group]
        for path, ops in (spec.get("paths") or {}).items():
            if path not in merged["paths"]:
                merged["paths"][path] = ops
            else:
                # Merge per-method (first wins).
                for m, op in ops.items():
                    if m not in merged["paths"][path]:
                        merged["paths"][path][m] = op
        comp = spec.get("components") or {}
        for schema_name, schema in (comp.get("schemas") or {}).items():
            merged["components"]["schemas"].setdefault(schema_name, schema)

    return by_group


def parse_spec_to_tools(spec: dict[str, Any], group: str) -> list[ToolDef]:
    """Walk an OpenAPI spec's `paths` and emit one ToolDef per operation."""
    tools: list[ToolDef] = []
    used_names: set[str] = set()
    sources = spec.get("_sources", [])
    for path, ops in (spec.get("paths") or {}).items():
        if not isinstance(ops, dict):
            continue
        for method in ("get", "post", "put", "patch", "delete"):
            op = ops.get(method)
            if not isinstance(op, dict):
                continue
            tool = _build_tool_def(group, method, path, op, used_names, sources=sources)
            tools.append(tool)
            used_names.add(tool.name)
    return tools


def generate_tool_module(tool: ToolDef) -> str:
    """Render Python source for one tool module."""
    return _render_tool_source(tool)


def regenerate_all() -> dict[str, int]:
    """Run the full pipeline. Returns `{group: tool_count_written}`."""
    print("Fetching OpenAPI specs...")
    specs_by_group = fetch_openapi_specs()

    counts: dict[str, int] = {}

    # Stable group ordering matching KNOWN_GROUPS.
    for group in KNOWN_GROUPS:
        spec = specs_by_group.get(group)
        if spec is None:
            _write_empty_group_package(group)
            counts[group] = 0
            continue

        tools = parse_spec_to_tools(spec, group)
        # Defensive dedup by tool name.
        seen: set[str] = set()
        unique: list[ToolDef] = []
        for t in tools:
            if t.name in seen:
                continue
            seen.add(t.name)
            unique.append(t)

        _write_group_package(group, unique)
        counts[group] = len(unique)

    return counts


# --------------------------------------------------------------------------- #
# Internals — discovery                                                       #
# --------------------------------------------------------------------------- #


def _http_get_bytes(url: str) -> bytes:
    """Simple HTTP GET with a 30s timeout — no retry (dev-only path)."""
    req = urllib.request.Request(url, headers={"User-Agent": "brightdata-mcp-full-codegen/0.1"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def _discover_spec_urls() -> dict[str, str]:
    """Parse llms.txt's `## OpenAPI Specs` section. Returns `{stem: url}`."""
    cache = SPECS_DIR / "llms.txt"
    if not cache.exists():
        cache.write_bytes(_http_get_bytes(LLMS_TXT_URL))
    content = cache.read_text()
    if "## OpenAPI Specs" not in content:
        return {}
    section = content.split("## OpenAPI Specs", 1)[1]
    pairs = re.findall(r"-\s*\[([^\]]+)\]\(([^)]+)\)", section)
    return {name: url for name, url in pairs}


# --------------------------------------------------------------------------- #
# Internals — IR construction                                                 #
# --------------------------------------------------------------------------- #


def _build_tool_def(
    group: str,
    method: str,
    path: str,
    op: dict[str, Any],
    used_names: set[str],
    sources: list[str],
) -> ToolDef:
    summary = (op.get("summary") or "").strip()
    description = (op.get("description") or "").strip()
    operation_id = (op.get("operationId") or "").strip()

    name = _make_tool_name(group, method, path, operation_id, used_names)

    parameters = [p for p in (op.get("parameters") or []) if isinstance(p, dict)]
    has_request_body = "requestBody" in op and isinstance(op["requestBody"], dict)

    is_write = method.lower() in ("post", "put", "patch", "delete")

    docs_url = _docs_url_for(group, path, method)

    return ToolDef(
        name=name,
        group=group,
        method=method.upper(),
        path=path,
        summary=summary,
        description=description,
        docs_url=docs_url,
        parameters=parameters,
        has_request_body=has_request_body,
        is_write=is_write,
        spec_source=",".join(sources),
    )


def _make_tool_name(
    group: str,
    method: str,
    path: str,
    operation_id: str,
    used_names: set[str],
) -> str:
    """Deterministic snake_case tool name: `bd_<group>_<verb>_<resource>` heuristic."""
    if operation_id:
        base = _to_snake(operation_id)
    else:
        verb_map = {
            "GET": "get",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete",
        }
        verb = verb_map.get(method.upper(), method.lower())

        # Path → tokens. Replace {param} with `by_<param>` for readability.
        clean = re.sub(r"\{([^}]+)\}", lambda m: f"by_{m.group(1)}", path)
        tokens = [t for t in re.split(r"[/\-_]+", clean) if t]
        slug = _to_snake("_".join(tokens))

        path_low = path.lower()
        if method.upper() == "GET":
            # If GET on a collection-y path, use `list`.
            if (
                path_low.endswith("/list")
                or path_low.endswith("s")
                or path_low.endswith("/searches")
                or path_low.endswith("/dumps")
            ) and "by_" not in slug:
                verb = "list"
            elif (
                path_low.endswith("/status")
                or path_low.endswith("/balance")
                or path_low.endswith("/cost")
                or path_low.endswith("/permissions")
                or path_low.endswith("/passwords")
                or path_low.endswith("/bw")
                or path_low.endswith("/cities")
                or path_low.endswith("/countrieslist")
            ):
                verb = "get"
        base = f"{verb}_{slug}" if slug else verb

    name = f"bd_{group}_{base}"
    name = _to_snake(name)
    name = re.sub(r"_{2,}", "_", name).strip("_")

    if keyword.iskeyword(name) or not name.isidentifier():
        name = f"{name}_op"

    if name in used_names:
        i = 2
        while f"{name}_{i}" in used_names:
            i += 1
        name = f"{name}_{i}"

    return name


def _to_snake(s: str) -> str:
    """Convert any string (camelCase, kebab-case, slashed paths) to snake_case."""
    if not s:
        return ""
    s = re.sub(r"[/\-\s\.]+", "_", s)
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = s.lower()
    s = re.sub(r"[^a-z0-9_]", "_", s)
    s = re.sub(r"_{2,}", "_", s).strip("_")
    return s


def _docs_url_for(group: str, path: str, method: str) -> str:
    """Best-effort link to BD docs. Falls back to api-reference index."""
    _ = (group, path, method)
    return "https://docs.brightdata.com/api-reference/"


# --------------------------------------------------------------------------- #
# Internals — code emission                                                   #
# --------------------------------------------------------------------------- #


def _python_type_for_schema(schema: dict[str, Any] | None) -> str:
    """Return a Python type annotation for a (best-effort) parameter schema.

    Conservative — falls back to `str` for anything ambiguous, since most BD
    query/path params are stringly-typed in practice.
    """
    if not schema or not isinstance(schema, dict):
        return "str"
    t = schema.get("type")
    if t == "integer":
        return "int"
    if t == "number":
        return "float"
    if t == "boolean":
        return "bool"
    if t == "array":
        return "list[Any]"
    if t == "object":
        return "dict[str, Any]"
    return "str"


def _render_tool_source(tool: ToolDef) -> str:
    """Emit Python source for one tool module."""
    path_params: list[dict[str, Any]] = []
    query_params: list[dict[str, Any]] = []
    for p in tool.parameters:
        loc = p.get("in")
        if loc == "path":
            path_params.append(p)
        elif loc == "query":
            query_params.append(p)
        # header / cookie params skipped — handled by client._headers()

    args: list[str] = []
    docstring_args: list[str] = []
    has_any_args = False

    used_arg_names: set[str] = set()

    for p in path_params:
        pname = p.get("name") or "param"
        py_name = _safe_arg_name(pname, used_arg_names)
        used_arg_names.add(py_name)
        py_type = _python_type_for_schema(p.get("schema") or {})
        args.append(f"{py_name}: {py_type}")
        desc = (p.get("description") or "Path parameter.").strip().replace("\n", " ")
        docstring_args.append(f"        {py_name}: {desc}")
        has_any_args = True

    # Required query params first (no default), then optional.
    for p in sorted(query_params, key=lambda x: 0 if x.get("required") else 1):
        pname = p.get("name") or "param"
        py_name = _safe_arg_name(pname, used_arg_names)
        used_arg_names.add(py_name)
        py_type = _python_type_for_schema(p.get("schema") or {})
        if p.get("required"):
            args.append(f"{py_name}: {py_type}")
        else:
            args.append(f"{py_name}: {py_type} | None = None")
        desc = (p.get("description") or "Query parameter.").strip().replace("\n", " ")
        docstring_args.append(f"        {py_name}: {desc}")
        has_any_args = True

    if tool.has_request_body and tool.method in ("POST", "PUT", "PATCH"):
        args.append("body: dict[str, Any] | None = None")
        docstring_args.append("        body: JSON request body. See BD docs for schema.")
        has_any_args = True

    args_str = ", ".join(args)

    # Build docstring lines
    docstring_lines: list[str] = []
    if tool.summary:
        docstring_lines.append(_one_line(tool.summary))
    elif tool.description:
        first_line = tool.description.split("\n", 1)[0].strip()
        docstring_lines.append(first_line[:200] if first_line else f"Call {tool.method} {tool.path}.")
    else:
        docstring_lines.append(f"Call {tool.method} {tool.path}.")

    if tool.description and tool.description != docstring_lines[0]:
        docstring_lines.append("")
        wrapped = textwrap.fill(_one_line(tool.description), width=88)
        for line in wrapped.split("\n"):
            docstring_lines.append(line.rstrip())

    docstring_lines.append("")
    docstring_lines.append(f"From: {tool.method} {tool.path}")
    docstring_lines.append(f"Docs: {tool.docs_url}")
    if tool.spec_source:
        docstring_lines.append(f"Source spec: {tool.spec_source}")

    if has_any_args:
        docstring_lines.append("")
        docstring_lines.append("Args:")
        docstring_lines.extend(docstring_args)

    docstring_lines.append("")
    docstring_lines.append("Returns:")
    docstring_lines.append(
        '    Parsed JSON response, or `{"error": str, "status_code": int, ...}` on failure.'
    )

    docstring = _format_docstring(docstring_lines)

    # Build call body
    call_body = _render_call_body(tool, path_params, query_params, used_arg_names)

    decorator_line = "@requires_write_enabled\n" if tool.is_write else ""
    safety_import = "from lib.safety import requires_write_enabled\n" if tool.is_write else ""

    src = f'''"""{tool.name} — auto-generated tool for {tool.method} {tool.path}.

Auto-generated by lib/codegen.py. DO NOT EDIT BY HAND.
To regenerate: `uv run python scripts/regenerate.py`.

Source spec: {tool.spec_source}
"""
# ruff: noqa
# pyright: ignore

from __future__ import annotations

from typing import Any

from lib.client import bd_request
{safety_import}
GROUP = "{tool.group}"
WRITES = {tool.is_write!r}


{decorator_line}async def {tool.name}({args_str}) -> dict[str, Any]:
{docstring}
{call_body}
'''
    return src


def _safe_arg_name(name: str, used: set[str]) -> str:
    n = _to_snake(name)
    if not n or not n.isidentifier() or keyword.iskeyword(n):
        n = f"{n}_arg" if n else "arg"
    base = n
    i = 2
    while n in used:
        n = f"{base}_{i}"
        i += 1
    return n


def _format_docstring(lines: list[str]) -> str:
    """Render a triple-quoted indented docstring (4-space indent)."""
    out = ['    """' + lines[0]]
    for ln in lines[1:]:
        if ln:
            out.append("    " + ln)
        else:
            out.append("")
    out.append('    """')
    return "\n".join(out)


def _one_line(s: str) -> str:
    return " ".join(s.split())


def _render_call_body(
    tool: ToolDef,
    path_params: list[dict[str, Any]],
    query_params: list[dict[str, Any]],
    used_arg_names: set[str],
) -> str:
    """Emit the function body that calls bd_request."""
    indent = "    "
    body: list[str] = []

    # path → f-string; we need to map original {paramName} → {py_name}
    if path_params:
        rendered_path = tool.path
        # Track py names assigned to path params (in same order they appear).
        # We re-derive using same logic _safe_arg_name uses, but unique within the func.
        local_used: set[str] = set()
        for p in path_params:
            orig = p.get("name") or "param"
            py = _safe_arg_name(orig, local_used)
            local_used.add(py)
            rendered_path = rendered_path.replace("{" + orig + "}", "{" + py + "}")
        # Escape any literal { } in path that aren't from path params (rare).
        body.append(f'{indent}path = f"{rendered_path}"')
    else:
        body.append(f'{indent}path = "{tool.path}"')

    if query_params:
        body.append(f"{indent}params: dict[str, Any] = {{}}")
        local_used2: set[str] = set()
        # We must mirror the arg-name assignment we did above.
        # Path params get assigned first; then required query; then optional query.
        # Use the same machinery: assign path first, then query in same order.
        for p in path_params:
            local_used2.add(_safe_arg_name(p.get("name") or "param", local_used2))
        for p in sorted(query_params, key=lambda x: 0 if x.get("required") else 1):
            orig = p.get("name") or "param"
            py = _safe_arg_name(orig, local_used2)
            local_used2.add(py)
            if p.get("required"):
                body.append(f'{indent}params["{orig}"] = {py}')
            else:
                body.append(f"{indent}if {py} is not None:")
                body.append(f'{indent}    params["{orig}"] = {py}')
        params_kw = "params=params"
    else:
        params_kw = ""

    json_kw = (
        "json=body"
        if tool.has_request_body and tool.method in ("POST", "PUT", "PATCH")
        else ""
    )

    kwargs = ", ".join(k for k in (params_kw, json_kw) if k)
    if kwargs:
        body.append(f'{indent}return await bd_request("{tool.method}", path, {kwargs})')
    else:
        body.append(f'{indent}return await bd_request("{tool.method}", path)')

    # Avoid pyright "unused" warning when used_arg_names came in non-empty: we use it
    # implicitly via _safe_arg_name; nothing else to do.
    _ = used_arg_names

    return "\n".join(body)


# --------------------------------------------------------------------------- #
# Internals — file writing                                                    #
# --------------------------------------------------------------------------- #


def _write_group_package(group: str, tools: list[ToolDef]) -> None:
    """Write tools/<group>/<tool>.py + __init__.py for a group.

    Preserves any existing file containing SMOKE_MARKER (hand-written tools).
    """
    group_dir = TOOLS_DIR / group
    group_dir.mkdir(parents=True, exist_ok=True)

    # 1. Wipe previously-generated files (anything that's NOT smoke-marked).
    smoke_files = _smoke_files_in(group_dir)
    for existing in group_dir.glob("*.py"):
        if existing.name == "__init__.py":
            continue
        if existing.stem in smoke_files:
            continue
        existing.unlink()

    # 2. Write generated tools (skip names that collide with smoke-marked files).
    written_tool_names: list[str] = []
    for tool in tools:
        if tool.name in smoke_files:
            written_tool_names.append(tool.name)
            continue
        target = group_dir / f"{tool.name}.py"
        target.write_text(_render_tool_source(tool))
        written_tool_names.append(tool.name)

    # 3. Add smoke-tools whose names weren't generated (they remain).
    for sname in smoke_files:
        if sname not in written_tool_names:
            written_tool_names.append(sname)

    (group_dir / "__init__.py").write_text(_render_group_init(group, written_tool_names))


def _smoke_files_in(group_dir: Path) -> list[str]:
    """Return list of tool names (file stems) that are smoke-marked in this group."""
    out: list[str] = []
    for f in group_dir.glob("*.py"):
        if f.name == "__init__.py":
            continue
        try:
            if SMOKE_MARKER in f.read_text():
                out.append(f.stem)
        except OSError:
            pass
    return out


def _render_group_init(group: str, tool_names: list[str]) -> str:
    """Emit the __init__.py for a group package."""
    sorted_names = sorted(tool_names)

    if not sorted_names:
        return f'''"""{group} group — no tools (spec not mapped or empty)."""
# ruff: noqa
# pyright: ignore

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_tools(mcp: FastMCP) -> None:
    """No-op — this group has no tools yet."""
    _ = mcp
    return None


__all__ = ["register_tools"]
'''

    imports = "\n".join(f"from .{n} import {n}" for n in sorted_names)
    registrations = "\n".join(f"    mcp.tool()({n})" for n in sorted_names)
    all_list = ",\n".join(f'    "{n}"' for n in [*sorted_names, "register_tools"])

    return f'''"""{group} group — auto-generated tool registrations.

Auto-generated by lib/codegen.py. DO NOT EDIT BY HAND.
To regenerate: `uv run python scripts/regenerate.py`.

Hand-written smoke tools (with `# SMOKE-TOOL: hand-written` marker) are preserved.
"""
# ruff: noqa
# pyright: ignore

from __future__ import annotations

from typing import TYPE_CHECKING

{imports}

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_tools(mcp: FastMCP) -> None:
    """Register all {group} tools with the FastMCP instance."""
{registrations}


__all__ = [
{all_list},
]
'''


def _write_empty_group_package(group: str) -> None:
    """Ensure a group package exists even when no spec maps to it.

    Always rewrites __init__.py for empty groups so generator changes propagate.
    """
    group_dir = TOOLS_DIR / group
    group_dir.mkdir(parents=True, exist_ok=True)
    init_path = group_dir / "__init__.py"
    init_path.write_text(_render_group_init(group, []))
