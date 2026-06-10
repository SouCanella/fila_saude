#!/usr/bin/env python3
"""Parse docs/tech-debt.md → tech_debt.data.json."""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CRITICAL = re.compile(r"crit(i|í)?ca|critical", re.I)


def resolve_tech_debt_path(root: Path) -> Path:
    for rel in ("docs/tech-debt.md", "tech-debt.md"):
        p = root / rel
        if p.exists():
            return p
    return root / "docs/tech-debt.md"


def parse_tech_debt_table(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line or "ID" in line:
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if len(parts) < 8 or parts[0] in ("—", "-", ""):
            continue
        rows.append(
            {
                "id": parts[0],
                "description": parts[1],
                "risk": parts[3],
                "req": parts[4],
                "status": parts[7],
            }
        )
    return rows


def _norm(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def is_critical_open(row: dict) -> bool:
    status = _norm(row.get("status") or "")
    if status in ("closed", "done", "resolved", "fechada", "resolvida"):
        return False
    risk = _norm(row.get("risk") or "")
    return "critica" in risk or "critical" in risk


def build_payload(root: Path) -> dict:
    path = resolve_tech_debt_path(root)
    items = parse_tech_debt_table(path)
    critical = [r for r in items if is_critical_open(r)]
    return {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "source": str(path.relative_to(root)) if path.is_relative_to(root) else str(path),
        "items": items,
        "report": {
            "total": len(items),
            "critical_open_count": len(critical),
            "critical_items": critical,
            "has_critical_blocker": len(critical) > 0,
        },
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
