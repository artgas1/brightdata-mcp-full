"""Codegen pipeline skeleton — A2 implements in INFRA-162.

This module will fetch BD's 31 OpenAPI specs (referenced from
https://docs.brightdata.com/llms.txt), parse them into typed Pydantic models,
and emit one `tools/{group}/{tool_name}.py` file per operation.

Round 1 (A1) only ships the interface — function signatures, docstrings, and
NotImplementedError bodies. Round 2 (A2) fills in the implementation.

Public surface (used by `scripts/regenerate.py`):
    - fetch_openapi_specs() → mapping of {group_name: parsed_spec_dict}
    - parse_spec_to_tools(spec, group) → list of ToolDef intermediate records
    - generate_tool_module(tool) → str (Python source for a single tool file)
    - regenerate_all() → dict[str, int] (group → tool count generated)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolDef:
    """Intermediate representation of one MCP tool, derived from one OpenAPI operation.

    Populated by parse_spec_to_tools(); consumed by generate_tool_module().
    """

    name: str
    """Snake_case tool function name, e.g. `bd_zone_list`."""

    group: str
    """Group identifier, e.g. `account_management`. Must be in groups.KNOWN_GROUPS."""

    method: str
    """HTTP method (GET/POST/PUT/DELETE)."""

    path: str
    """API path with `/` prefix and `{param}` placeholders preserved."""

    summary: str
    """One-line summary lifted from OpenAPI `summary` or `description` field."""

    description: str
    """Multi-line description for the docstring — `description` from OpenAPI."""

    docs_url: str
    """Link to the BD docs page for this operation, surfaced in docstring."""

    parameters: list[dict[str, Any]] = field(default_factory=list)
    """OpenAPI parameter definitions (path/query). Each: {name, in, required, schema}."""

    request_body_schema: dict[str, Any] | None = None
    """OpenAPI request body schema if the operation has one (POST/PUT only)."""

    response_schema: dict[str, Any] | None = None
    """OpenAPI 200-response schema. Used to generate the Pydantic response model."""

    is_write: bool = False
    """True if method is POST/PUT/DELETE — wrapped in `@requires_write_enabled`."""


def fetch_openapi_specs() -> dict[str, dict[str, Any]]:
    """Fetch all 31 OpenAPI specs from docs.brightdata.com and parse to dicts.

    Discovers spec URLs from `https://docs.brightdata.com/llms.txt`, fetches each,
    parses YAML/JSON, and returns a mapping `{group_name: parsed_openapi_dict}`.

    Caches raw specs to `specs/openapi/<group>.yaml` (gitignored) for offline regen.

    Returns:
        Mapping of group identifier (account_management, proxy_manager, ...) to
        the parsed OpenAPI 3.x document for that group.

    Raises:
        NotImplementedError: A1 ships skeleton only — A2 implements.
    """
    raise NotImplementedError("Implemented in INFRA-162 by A2 codegen-engineer")


def parse_spec_to_tools(spec: dict[str, Any], group: str) -> list[ToolDef]:
    """Walk an OpenAPI spec's `paths` and emit one ToolDef per operation.

    For each `paths[path][method]` operation:
        - Build snake_case tool name (`bd_<verb>_<resource>` heuristic).
        - Extract summary/description/parameters/responses.
        - Mark `is_write=True` for non-GET methods.

    Args:
        spec: Parsed OpenAPI 3.x dict (as returned by fetch_openapi_specs).
        group: Group identifier this spec belongs to.

    Returns:
        List of ToolDef records, one per operation.

    Raises:
        NotImplementedError: A1 ships skeleton only — A2 implements.
    """
    raise NotImplementedError("Implemented in INFRA-162 by A2 codegen-engineer")


def generate_tool_module(tool: ToolDef) -> str:
    """Render a single tool's Python source from its ToolDef.

    Output format (one file per tool):
        - Imports from lib.client, lib.safety, lib.types.<group>
        - Pydantic param/response models (or import from lib.types)
        - Async function with type-annotated args matching the OpenAPI parameters
        - Docstring built from summary + description + docs_url
        - `@requires_write_enabled` decorator if tool.is_write
        - Body: call bd_request and return parsed result

    Args:
        tool: A ToolDef produced by parse_spec_to_tools.

    Returns:
        Python source code string ready to be written to
        `tools/<group>/<tool.name>.py`.

    Raises:
        NotImplementedError: A1 ships skeleton only — A2 implements.
    """
    raise NotImplementedError("Implemented in INFRA-162 by A2 codegen-engineer")


def regenerate_all() -> dict[str, int]:
    """Run the full pipeline: fetch specs, parse, generate, write to disk.

    Side effects:
        - Caches OpenAPI specs to `specs/openapi/`.
        - Generates Pydantic types in `lib/types/<group>.py`.
        - Generates tool modules in `tools/<group>/<tool>.py`.
        - Generates `tools/<group>/__init__.py` that exposes `register_tools(mcp)`.
        - Idempotent — overwrites existing generated files.

    Returns:
        Mapping `{group: tool_count_written}` for reporting.

    Raises:
        NotImplementedError: A1 ships skeleton only — A2 implements.
    """
    raise NotImplementedError("Implemented in INFRA-162 by A2 codegen-engineer")
