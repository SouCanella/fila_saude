#!/usr/bin/env python3
"""Compare built quality-health JSON to HEAD (ignore built_at)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "docs/meta/quality-health/quality-health.data.json"
VOLATILE = frozenset({"built_at"})


def strip_volatile(obj):
    if isinstance(obj, dict):
        return {k: strip_volatile(v) for k, v in obj.items() if k not in VOLATILE}
    if isinstance(obj, list):
        return [strip_volatile(x) for x in obj]
    return obj


def main() -> int:
    if not PATH.exists():
        print(f"ERRO: {PATH} ausente", file=sys.stderr)
        return 1
    built = strip_volatile(json.loads(PATH.read_text(encoding="utf-8")))
    try:
        head_raw = subprocess.check_output(
            ["git", "show", f"HEAD:{PATH.relative_to(ROOT)}"],
            cwd=ROOT,
            text=True,
        )
        committed = strip_volatile(json.loads(head_raw))
    except subprocess.CalledProcessError:
        print("OK: JSON novo (sem versão em HEAD)")
        return 0
    if built != committed:
        print(
            "ERRO: quality-health.data.json difere do commit — "
            "rode make quality-build e git add/commit",
            file=sys.stderr,
        )
        return 1
    print("OK: quality-health.data.json alinhado ao HEAD")
    return 0


if __name__ == "__main__":
    sys.exit(main())
