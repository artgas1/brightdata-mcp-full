"""Generate docs/groups.md — full catalog of all bd_* tools by group.

Walks tools/<group>/bd_*.py, parses the first non-blank line of each tool's
module docstring, and emits a markdown catalog. Re-runnable any time after
codegen — output is deterministic from the tool tree.

Usage:
    uv run python scripts/generate_groups_doc.py > docs/groups.md
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
TOOLS_DIR = REPO_ROOT / "tools"


def first_docstring_line(py_file: Path) -> str:
    """Return the first non-blank line of a Python file's module docstring.

    Strips the leading `bd_xxx — ` prefix if present so the description reads
    cleanly in a tool catalog table.
    """
    try:
        source = py_file.read_text(encoding="utf-8")
        tree = ast.parse(source)
        docstring = ast.get_docstring(tree) or ""
    except (SyntaxError, OSError):
        return "(no docstring)"

    for raw_line in docstring.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # Strip leading "bd_xxx — " prefix
        stem = py_file.stem
        if line.startswith(f"{stem} —"):
            line = line[len(f"{stem} —") :].strip()
        elif line.startswith(f"{stem} -"):
            line = line[len(f"{stem} -") :].strip()
        return line
    return "(no docstring)"


def is_smoke_tool(py_file: Path) -> bool:
    """Detect hand-written smoke tools by their marker."""
    try:
        return "# SMOKE-TOOL: hand-written" in py_file.read_text(encoding="utf-8")
    except OSError:
        return False


def writes_flag(py_file: Path) -> bool:
    """Check WRITES = True in the tool module."""
    try:
        return "WRITES = True" in py_file.read_text(encoding="utf-8")
    except OSError:
        return False


def main() -> int:
    out = sys.stdout

    out.write("# Tool catalog — 149 tools across 15 groups\n\n")
    out.write(
        "Auto-generated from `tools/*/bd_*.py` by "
        "`scripts/generate_groups_doc.py`. Regenerate after any codegen run.\n\n"
    )
    out.write(
        "**Legend:** "
        "`smoke` = hand-written bootstrap tool (preserved across regen). "
        "`write` = mutating op, gated by `BD_ENABLE_WRITES=true`.\n\n"
    )

    # Top-level summary
    groups = sorted(p for p in TOOLS_DIR.iterdir() if p.is_dir())
    out.write("## Summary\n\n")
    out.write("| Group | Tools |\n|---|---:|\n")
    total = 0
    for group_dir in groups:
        tools = sorted(group_dir.glob("bd_*.py"))
        out.write(f"| [`{group_dir.name}`](#{group_dir.name}) | {len(tools)} |\n")
        total += len(tools)
    out.write(f"| **Total** | **{total}** |\n\n")

    # Per-group tables
    for group_dir in groups:
        tools = sorted(group_dir.glob("bd_*.py"))
        out.write(f"## {group_dir.name}\n\n")
        out.write(f"_{len(tools)} tools._\n\n")
        if not tools:
            out.write("(no tools — group reserved for future endpoints)\n\n")
            continue
        out.write("| Tool | Description | Flags |\n|---|---|---|\n")
        for tool in tools:
            desc = first_docstring_line(tool)
            # Escape pipe chars in description for markdown table safety
            desc = desc.replace("|", "\\|")
            flags = []
            if is_smoke_tool(tool):
                flags.append("smoke")
            if writes_flag(tool):
                flags.append("write")
            flag_str = ", ".join(flags) if flags else "—"
            out.write(f"| `{tool.stem}` | {desc} | {flag_str} |\n")
        out.write("\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
