#!/usr/bin/env python3
"""Security health JSON — checklist global + REQs sensíveis."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "scripts"))
from quality_spec_parser import (  # noqa: E402
    find_spec_path,
    load_yaml,
    parse_backlog,
    parse_spec,
    set_paths,
)

MODULE_HELP = {
    "title": "Segurança do projeto",
    "summary": (
        "Consolida o checklist global de entrega (docs/security/) com REQs marcados "
        "como sensíveis ou que exigem camada security na spec."
    ),
    "sources": [
        "docs/security/security-checklist.md",
        "docs/specs/REQ-*.md (frontmatter sensitive + seção threat model)",
    ],
    "actions": [
        "Completar checklist global antes de merge",
        "REQ sensível sem threat model → adicionar seção na spec",
        "REQ com camada security sem spec → criar spec approved",
    ],
}


def parse_markdown_checklist(path: Path) -> list[dict]:
    if not path.exists():
        return []
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^- \[([ xX])\]\s+(.+)$", line.strip())
        if m:
            items.append({"label": m.group(2).strip(), "checked": m.group(1).lower() == "x"})
    return items


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end < 0:
        return {}
    try:
        import yaml  # type: ignore

        meta = yaml.safe_load(text[3:end]) or {}
        return meta if isinstance(meta, dict) else {}
    except Exception:
        return {}


def has_threat_model(spec_path: Path) -> bool:
    if not spec_path.exists():
        return False
    text = spec_path.read_text(encoding="utf-8").lower()
    return "threat model" in text or "threat-model" in text or "## ameaças" in text


def resolve_checklist_path(root: Path) -> Path:
    for candidate in (
        root / "docs/security/security-checklist.md",
        ROOT / "docs/security/security-checklist.md",
    ):
        if candidate.exists():
            return candidate
    return root / "docs/security/security-checklist.md"


def parse_change_type_checklists(root: Path) -> list[dict]:
    for rel in ("docs/security/security-by-change-type.md", "security/security-by-change-type.md"):
        path = root / rel
        if path.exists():
            break
    else:
        return []
    sections: list[dict] = []
    current: dict | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if current:
                sections.append(current)
            current = {"section": line[3:].strip(), "items": [], "checked": 0, "total": 0}
        elif current and re.match(r"^-\s+\[", line.strip()):
            checked = "[x]" in line.lower() or "[X]" in line
            current["items"].append({"label": re.sub(r"^-\s+\[[ xX]\]\s*", "", line.strip()), "checked": checked})
            current["total"] += 1
            if checked:
                current["checked"] += 1
    if current:
        sections.append(current)
    return sections


def parse_lgpd_filled(root: Path) -> dict:
    for rel in ("docs/security/privacy-lgpd.md", "security/privacy-lgpd.md"):
        path = root / rel
        if path.exists():
            break
    else:
        return {"filled": False, "pii_rows": 0}
    text = path.read_text(encoding="utf-8")
    rows = 0
    filled_rows = 0
    in_table = False
    for line in text.splitlines():
        if "| Categoria |" in line:
            in_table = True
            continue
        if in_table and line.startswith("|") and "---" not in line:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if parts and parts[0] not in ("_preencher_", "—", ""):
                filled_rows += 1
            if parts and parts[0]:
                rows += 1
        elif in_table and not line.startswith("|"):
            break
    return {"filled": filled_rows > 0, "pii_rows": filled_rows}


def build_compliance_block(root: Path) -> dict:
    lgpd = parse_lgpd_filled(root)
    change_types = parse_change_type_checklists(root)
    ct_ok = all(s["checked"] == s["total"] for s in change_types if s["total"]) if change_types else False
    return {
        "lgpd": lgpd,
        "change_types": change_types,
        "ok": lgpd["filled"] and (ct_ok or not change_types),
    }


def build_payload(root: Path) -> dict:
    checklist_path = resolve_checklist_path(root)
    checklist = parse_markdown_checklist(checklist_path)
    checked = sum(1 for i in checklist if i["checked"])
    total = len(checklist) or 1

    reqs = []
    gaps = []
    for br in parse_backlog():
        req_id = br["req_id"]
        spec = parse_spec(req_id)
        path = find_spec_path(req_id)
        sensitive = False
        if path and path.exists():
            sensitive = bool(parse_frontmatter(path.read_text(encoding="utf-8")).get("sensitive"))
        sec_layer = (spec.get("required_layers") or {}).get("security", False)
        threat = has_threat_model(path) if path else False
        item = {
            "req_id": req_id,
            "title": br.get("title"),
            "priority": br.get("priority"),
            "req_kind": br.get("req_kind", "functional"),
            "sensitive": sensitive,
            "security_required": sec_layer,
            "has_threat_model": threat,
            "spec_status": spec.get("status"),
        }
        reqs.append(item)
        if sensitive and not threat:
            gaps.append({**item, "gap": "Threat model ausente na spec"})
        if sec_layer and not spec.get("exists"):
            gaps.append({**item, "gap": "Spec ausente com camada security marcada"})

    global_gap = checked < total
    compliance = build_compliance_block(root)
    return {
        "built_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "module_help": MODULE_HELP,
        "checklist_path": str(checklist_path.relative_to(root)) if checklist_path.exists() and str(checklist_path).startswith(str(root)) else str(checklist_path),
        "checklist": checklist,
        "requirements": reqs,
        "gaps": gaps,
        "compliance": compliance,
        "report": {
            "checklist_pct": round((checked / total) * 100),
            "checklist_ok": checked,
            "checklist_total": len(checklist),
            "global_checklist_complete": not global_gap,
            "sensitive_count": sum(1 for r in reqs if r["sensitive"]),
            "sensitive_gaps": len([g for g in gaps if g.get("sensitive")]),
            "gap_count": len(gaps) + (1 if global_gap else 0),
            "compliance_ok": compliance.get("ok", False),
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--config", type=Path)
    p.add_argument("--backlog", type=Path)
    p.add_argument("--specs-dir", type=Path)
    p.add_argument("--json", type=Path, required=True)
    args = p.parse_args()
    root = args.root.resolve()
    set_paths(
        root=root,
        config=args.config or root / "project.config.yaml",
        backlog=args.backlog or root / "docs/backlog/mvp-backlog.md",
        specs_dir=args.specs_dir or root / "docs/specs",
    )
    payload = build_payload(root)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
