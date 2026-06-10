#!/usr/bin/env python3
"""Parse docs/delivery-log.md → delivery.data.json for Project Hub."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "scripts"))
from modelo_ids import DELIVERY_HEADER_RE, find_req_ids, parse_phase_from_block  # noqa: E402


def is_placeholder_entry(card_id: str, status: str, started_at: str | None, title: str) -> bool:
    """Ignora blocos de exemplo (templates/new-project) que não são entregas reais."""
    if card_id == "CARD-XXX":
        return True
    if "|" in status:
        return True
    if started_at and "YYYY-MM-DD" in started_at.upper():
        return True
    if title.startswith("[") and title.endswith("]"):
        return True
    return False


def resolve_delivery_log(root: Path) -> Path:
    for candidate in (root / "docs/delivery-log.md", root / "delivery-log.md"):
        if candidate.exists():
            return candidate
    return root / "docs/delivery-log.md"


def parse_delivery_log(path: Path) -> list[dict]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    entries = []
    for block in re.split(r"\n---+\n", text):
        header = DELIVERY_HEADER_RE.search(block)
        if not header:
            continue
        card_id = header.group(1).upper()
        title = (header.group(2) or "").strip()
        status_m = re.search(r"^Status:\s*(.+)$", block, re.M | re.I)
        status = status_m.group(1).strip() if status_m else "unknown"
        req_ids = find_req_ids(block)
        red_green = re.search(r"Red\s*→\s*Green:\s*(.+)$", block, re.M | re.I)
        start_m = re.search(r"Data/hora início:\s*(.+)$", block, re.M | re.I)
        end_m = re.search(r"Data/hora fim:\s*(.+)$", block, re.M | re.I)
        branch_m = re.search(r"^Branch:\s*(.+)$", block, re.M | re.I)
        pr_m = re.search(r"^PR/MR:\s*(.+)$", block, re.M | re.I)
        phase = parse_phase_from_block(block)
        card_path_m = re.search(r"Arquivo:\s*(.+)$", block, re.M | re.I)
        started_at = start_m.group(1).strip() if start_m else None
        if is_placeholder_entry(card_id, status, started_at, title):
            continue
        entries.append(
            {
                "card_id": card_id,
                "title": title or card_id,
                "status": status,
                "req_ids": [r.upper() for r in req_ids],
                "tdd_red_green": red_green.group(1).strip() if red_green else None,
                "started_at": started_at,
                "ended_at": end_m.group(1).strip() if end_m else None,
                "branch": branch_m.group(1).strip() if branch_m else None,
                "pr": pr_m.group(1).strip() if pr_m else None,
                "phase": phase,
                "card_path": card_path_m.group(1).strip() if card_path_m else None,
            }
        )
    return entries


def build_payload(root: Path) -> dict:
    log_path = resolve_delivery_log(root)
    entries = parse_delivery_log(log_path)
    return {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "source": str(log_path.relative_to(root)) if log_path.is_relative_to(root) else str(log_path),
        "entries": entries,
        "report": {
            "total": len(entries),
            "completed": sum(1 for e in entries if "conclu" in e.get("status", "").lower()),
            "in_progress": sum(1 for e in entries if "andamento" in e.get("status", "").lower()),
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
