"""Regenerate all auto-generated tools by re-running the codegen pipeline.

Usage:
    uv run python scripts/regenerate.py

This is the entry point users run after Bright Data updates their OpenAPI
specs. It delegates to `lib.codegen.regenerate_all()` which (after A2 lands
in INFRA-162) will fetch the 31 specs, parse them, and emit ~350 tool files.

A1 ships this as a thin wrapper — it will surface NotImplementedError until
A2 implements the codegen pipeline.
"""

from __future__ import annotations

import sys

from lib.codegen import regenerate_all


def main() -> int:
    try:
        counts = regenerate_all()
    except NotImplementedError as e:
        print(f"codegen not yet implemented: {e}", file=sys.stderr)
        print("This will be filled in by A2 in INFRA-162.", file=sys.stderr)
        return 2

    total = sum(counts.values())
    print(f"Regenerated {total} tools across {len(counts)} groups:")
    for group, n in sorted(counts.items()):
        print(f"  {group}: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
