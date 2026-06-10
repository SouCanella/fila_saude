#!/usr/bin/env python3
"""Design readiness JSON — status visual + APPROVAL checklist geral."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MODULE_HELP = {
    "title": "Design readiness",
    "summary": (
        "Antes de implementar React/Vue/etc., o MVP precisa de mocks HTML aprovados em "
        "design-references/. Este módulo mostra status de aprovação, checklist e links para abrir cada tela mockada."
    ),
    "sources": [
        "project.config.yaml → design.status, design.screens",
        "design-references/APPROVAL.md",
        "design-references/screens/*.html",
    ],
    "gate": "Framework de UI só após design.status == approved (rule 000-onboarding-gate).",
}


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        import yaml  # type: ignore
    except ImportError:
        print("ERRO: PyYAML necessário", file=sys.stderr)
        sys.exit(1)
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


def preview_url(html_path: str | None) -> str | None:
    if not html_path:
        return None
    return "/" + html_path.lstrip("/")


def parse_general_checklist(approval_path: Path) -> list[dict]:
    if not approval_path.exists():
        return []
    lines = approval_path.read_text(encoding="utf-8").splitlines()
    in_general = False
    items = []
    for line in lines:
        if re.search(r"##\s+checklist geral", line, re.I):
            in_general = True
            continue
        if in_general and line.startswith("## "):
            break
        if in_general:
            m = re.match(r"^- \[([ xX])\]\s+(.+)$", line.strip())
            if m:
                items.append({"label": m.group(2).strip(), "checked": m.group(1).lower() == "x"})
    return items


def parse_mock_table(approval_path: Path) -> list[dict]:
    if not approval_path.exists():
        return []
    rows = []
    in_table = False
    for line in approval_path.read_text(encoding="utf-8").splitlines():
        if "| Tela |" in line or "| tela |" in line.lower():
            in_table = True
            continue
        if in_table and line.startswith("|") and "---" not in line:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 3 and not parts[0].lower().startswith("exemplo"):
                checked = "[x]" in parts[2].lower() or parts[2].lower() == "true"
                html = parts[1]
                rows.append(
                    {
                        "screen": parts[0],
                        "file": html,
                        "mocks_complete": checked,
                        "preview_url": preview_url(html if "/" in html else f"design-references/{html}"),
                    }
                )
        if in_table and line.startswith("## "):
            break
    return rows


def resolve_approval(root: Path) -> Path:
    for candidate in (root / "design-references/APPROVAL.md", ROOT / "design-references/APPROVAL.md"):
        if candidate.exists():
            return candidate
    return root / "design-references/APPROVAL.md"


def enrich_screens(config_screens: list, mock_table: list[dict]) -> list[dict]:
    table_by_name = {r["screen"].lower(): r for r in mock_table}
    enriched = []
    for sc in config_screens:
        if not isinstance(sc, dict):
            continue
        html = sc.get("html")
        title = sc.get("title") or sc.get("id")
        table_row = table_by_name.get(str(title).lower()) or table_by_name.get(str(sc.get("id", "")).lower())
        enriched.append(
            {
                "id": sc.get("id"),
                "title": title,
                "html": html,
                "preview_url": preview_url(html),
                "mocks_complete": bool(sc.get("mocks_complete")),
                "linked_reqs": sc.get("linked_reqs") or [],
                "approval_row": table_row,
            }
        )
    return enriched


def build_payload(root: Path, config_path: Path) -> dict:
    cfg = load_yaml(config_path)
    design = cfg.get("design") or {}
    approval = resolve_approval(root)
    general = parse_general_checklist(approval)
    mock_table = parse_mock_table(approval)
    config_screens = design.get("screens") or []
    screens = enrich_screens(config_screens, mock_table)

    checked = sum(1 for i in general if i["checked"])
    total = len(general) or 1
    mocks_ok = all(s.get("mocks_complete") for s in screens) if screens else False
    status = design.get("status", "draft")
    ready = status == "approved" and mocks_ok

    gaps = []
    if status != "approved":
        gaps.append({"label": f"Design em status '{status}' (precisa approved)"})
    for sc in screens:
        if not sc.get("mocks_complete"):
            gaps.append({"label": f"Mock incompleto: {sc.get('id')}"})

    return {
        "built_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "module_help": MODULE_HELP,
        "design_status": status,
        "pattern_version": design.get("pattern_version"),
        "approved_at": design.get("approved_at"),
        "general_checklist": general,
        "mock_table": mock_table,
        "screens": screens,
        "gaps": gaps,
        "report": {
            "checklist_pct": round((checked / total) * 100),
            "ready_for_ui_impl": ready,
            "screens_count": len(screens),
            "screens_with_mock": sum(1 for s in screens if s.get("mocks_complete")),
            "gap_count": len(gaps),
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--config", type=Path)
    p.add_argument("--json", type=Path, required=True)
    args = p.parse_args()
    root = args.root.resolve()
    config = args.config or root / "project.config.yaml"
    payload = build_payload(root, config)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
