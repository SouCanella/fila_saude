#!/usr/bin/env python3
"""Retrospectives index + process benchmarks summary for Project Hub."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def parse_retro_index(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line or "Fase" in line:
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if len(parts) < 3 or not parts[0].startswith("FASE-"):
            continue
        rows.append(
            {
                "phase": parts[0],
                "status": parts[1].lower() if len(parts) > 1 else "pending",
                "file": parts[2] if len(parts) > 2 else "",
                "notes": parts[4] if len(parts) > 4 else "",
            }
        )
    return rows


def parse_benchmark_index(path: Path) -> dict:
    if not path.exists():
        return {"snapshot_count": 0, "snapshots": [], "medians": {}}
    text = path.read_text(encoding="utf-8")
    snapshots = []
    for line in text.splitlines():
        if "benchmark-" in line and line.strip().startswith("|"):
            parts = [p.strip().strip("`") for p in line.split("|")[1:-1]]
            if parts and parts[0].endswith(".json"):
                snapshots.append({"file": parts[0], "stack": parts[1] if len(parts) > 1 else ""})
    medians = {}
    in_table = False
    for line in text.splitlines():
        if "| Métrica |" in line:
            in_table = True
            continue
        if in_table and line.startswith("|") and "---" not in line:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 2 and parts[0].startswith("`"):
                key = parts[0].strip("`")
                medians[key] = parts[1]
        if in_table and line.startswith("## "):
            break
    return {
        "snapshot_count": len(snapshots),
        "snapshots": snapshots[:5],
        "medians": medians,
        "index_path": "docs/meta/process-benchmarks/index.md",
    }


def build_payload(root: Path) -> dict:
    retro_path = root / "docs/meta/retrospectives/index.md"
    if not retro_path.exists():
        retro_path = ROOT / "docs/meta/retrospectives/index.md"
    bench_path = root / "docs/meta/process-benchmarks/index.md"
    if not bench_path.exists():
        bench_path = ROOT / "docs/meta/process-benchmarks/index.md"

    retros = parse_retro_index(retro_path)
    pending = [r["phase"] for r in retros if r.get("status") == "pending"]
    benchmarks = parse_benchmark_index(bench_path)

    return {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "retrospectives": retros,
        "report": {
            "retro_total": len(retros),
            "retro_pending": len(pending),
            "pending_phases": pending,
        },
        "benchmarks": benchmarks,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--json", type=Path, required=True)
    args = p.parse_args()
    root = args.root.resolve()
    payload = build_payload(root)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
