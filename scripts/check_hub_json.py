#!/usr/bin/env python3
"""Compare built hub JSON files to HEAD, ignoring volatile fields."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATHS = [
    ROOT / "docs/meta/project-hub/data/hub.data.json",
    ROOT / "docs/meta/project-hub/data/journey.data.json",
]
ALL_JSON = [
    "hub.data.json",
    "process.data.json",
    "quality.data.json",
    "security.data.json",
    "a11y.data.json",
    "design.data.json",
    "delivery.data.json",
    "learning.data.json",
    "journey.data.json",
    "tech_debt.data.json",
    "openapi.data.json",
    "release.data.json",
]
VOLATILE = frozenset({"built_at"})


def strip_built_at(obj):
    if isinstance(obj, dict):
        return {k: strip_built_at(v) for k, v in obj.items() if k not in VOLATILE}
    if isinstance(obj, list):
        return [strip_built_at(x) for x in obj]
    return obj


def prepare_compare(data: dict, rel: Path) -> dict:
    """Remove campos voláteis por artefato (activity = git log + mtime)."""
    name = rel.name
    if name == "journey.data.json":
        data = {k: v for k, v in data.items() if k != "activity"}
    elif name == "hub.data.json":
        journey = data.get("journey")
        if isinstance(journey, dict):
            data = {**data, "journey": {k: v for k, v in journey.items() if k != "activity"}}
    return strip_built_at(data)


def check_path(path: Path) -> int:
    if not path.exists():
        print(f"ERRO: {path} ausente", file=sys.stderr)
        return 1
    rel = path.relative_to(ROOT)
    built = prepare_compare(json.loads(path.read_text(encoding="utf-8")), rel)
    try:
        head_raw = subprocess.check_output(
            ["git", "show", f"HEAD:{rel}"],
            cwd=ROOT,
            text=True,
        )
        committed = prepare_compare(json.loads(head_raw), rel)
    except subprocess.CalledProcessError:
        print(f"OK: {rel} novo (sem versão em HEAD)")
        return 0
    if built != committed:
        print(f"ERRO: {rel} difere do commit — rode make hub-build e git add/commit", file=sys.stderr)
        return 1
    print(f"OK: {rel} alinhado ao HEAD")
    return 0


def main() -> int:
    import os

    err = 0
    strict = os.environ.get("HUB_JSON_STRICT", "")
    if strict == "all":
        data_dir = ROOT / "docs/meta/project-hub/data"
        for name in ALL_JSON:
            err |= check_path(data_dir / name)
    else:
        for path in PATHS:
            err |= check_path(path)
    return err


if __name__ == "__main__":
    sys.exit(main())
