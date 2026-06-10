#!/usr/bin/env python3
"""Valida planos TDD nas specs (camadas marcadas ↔ tabelas ↔ arquivos)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from quality_spec_parser import _CTX, set_paths, validate_spec_plans  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path)
    p.add_argument("--backlog", type=Path)
    p.add_argument("--specs-dir", type=Path)
    p.add_argument("--strict", action="store_true", help="Exige Arquivo teste em todas as linhas aplicáveis")
    p.add_argument("--all-statuses", action="store_true", help="Inclui specs draft/in_review")
    args = p.parse_args()

    if args.root:
        _CTX["root"] = args.root.resolve()
    set_paths(root=args.root, backlog=args.backlog, specs_dir=args.specs_dir)

    issues = validate_spec_plans(strict=args.strict, approved_only=not args.all_statuses)
    errors = [i for i in issues if i.get("level") == "error"]
    warnings = [i for i in issues if i.get("level") != "error"]

    for item in issues:
        prefix = "ERRO" if item.get("level") == "error" else "AVISO"
        loc = item.get("req_id", "?")
        layer = item.get("layer")
        if layer:
            loc = f"{loc}/{layer}"
        print(f"{prefix}: {loc} — {item.get('message')}")

    if errors:
        print(f"Falha: {len(errors)} erro(s) no plano TDD", file=sys.stderr)
        return 1
    if warnings:
        print(f"OK com {len(warnings)} aviso(s)")
    else:
        print("OK: planos TDD coerentes com camadas marcadas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
