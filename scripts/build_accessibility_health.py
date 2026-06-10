#!/usr/bin/env python3
"""Accessibility health JSON — APPROVAL.md a11y + telas do config."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MODULE_HELP = {
    "title": "Acessibilidade (a11y)",
    "summary": (
        "A11y = tornar a interface utilizável por mais pessoas — leitores de tela, teclado, "
        "contraste, labels. Este painel lê o checklist WCAG básico em design-references/APPROVAL.md "
        "e o status dos mocks HTML por tela."
    ),
    "glossary": [
        {"term": "WCAG", "definition": "Diretrizes internacionais de acessibilidade web (níveis A, AA, AAA)."},
        {"term": "Contraste AA", "definition": "Texto legível sobre fundo — ratio mínimo ~4.5:1."},
        {"term": "Foco visível", "definition": "Indicador claro de qual elemento está ativo ao tabular."},
        {"term": "Labels", "definition": "Inputs associados a texto ou aria-label para leitores de tela."},
    ],
    "sources": [
        "design-references/APPROVAL.md (seção Acessibilidade)",
        "project.config.yaml → design.screens",
    ],
}

A11Y_LABELS = {
    "done": "OK",
    "partial": "Parcial",
    "pending": "Pendente",
    "unknown": "Não avaliado",
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


def parse_a11y_section(approval_path: Path) -> list[dict]:
    if not approval_path.exists():
        return []
    lines = approval_path.read_text(encoding="utf-8").splitlines()
    in_a11y = False
    items = []
    for line in lines:
        if re.search(r"##\s+acessibilidade", line, re.I):
            in_a11y = True
            continue
        if in_a11y and line.startswith("## "):
            break
        if in_a11y:
            m = re.match(r"^- \[([ xX])\]\s+(.+)$", line.strip())
            if m:
                items.append({"label": m.group(2).strip(), "checked": m.group(1).lower() == "x"})
    return items


def resolve_approval(root: Path) -> Path:
    for candidate in (root / "design-references/APPROVAL.md", ROOT / "design-references/APPROVAL.md"):
        if candidate.exists():
            return candidate
    return root / "design-references/APPROVAL.md"


def screen_a11y_status(sc: dict, checklist: list[dict]) -> str:
    explicit = sc.get("a11y_status")
    if explicit in A11Y_LABELS:
        return explicit
    if sc.get("mocks_complete") and checklist and all(i["checked"] for i in checklist):
        return "done"
    if sc.get("mocks_complete") and checklist and any(i["checked"] for i in checklist):
        return "partial"
    if sc.get("mocks_complete"):
        return "partial"
    return "unknown"


def build_payload(root: Path, config_path: Path) -> dict:
    cfg = load_yaml(config_path)
    approval = resolve_approval(root)
    checklist = parse_a11y_section(approval)
    checked = sum(1 for i in checklist if i["checked"])
    total = len(checklist) or 1

    screens = []
    for sc in (cfg.get("design") or {}).get("screens") or []:
        if not isinstance(sc, dict):
            continue
        html = sc.get("html")
        status = screen_a11y_status(sc, checklist)
        screens.append(
            {
                "id": sc.get("id"),
                "title": sc.get("title") or sc.get("id"),
                "html": html,
                "preview_url": preview_url(html),
                "mocks_complete": bool(sc.get("mocks_complete")),
                "a11y_status": status,
                "a11y_label": A11Y_LABELS.get(status, status),
                "linked_reqs": sc.get("linked_reqs") or [],
            }
        )

    gaps = []
    if checked < total:
        gaps.append({"type": "checklist", "label": "Checklist a11y incompleto em APPROVAL.md"})
    for sc in screens:
        if not sc.get("mocks_complete"):
            gaps.append({"type": "screen", "id": sc.get("id"), "label": f"Tela {sc.get('id')} sem mock completo"})
        elif sc.get("a11y_status") in ("pending", "partial", "unknown"):
            gaps.append(
                {
                    "type": "a11y",
                    "id": sc.get("id"),
                    "label": f"A11y {sc.get('a11y_label', 'pendente')} — {sc.get('title')}",
                }
            )

    return {
        "built_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "module_help": MODULE_HELP,
        "checklist": checklist,
        "screens": screens,
        "gaps": gaps,
        "report": {
            "checklist_pct": round((checked / total) * 100),
            "checklist_ok": checked,
            "checklist_total": len(checklist),
            "screens_total": len(screens),
            "screens_ready": sum(1 for s in screens if s.get("mocks_complete")),
            "a11y_partial": sum(1 for s in screens if s.get("a11y_status") == "partial"),
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
