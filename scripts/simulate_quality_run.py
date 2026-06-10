#!/usr/bin/env python3
"""Atualiza manual.yaml do demo simulando nova execução de testes."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_yaml(path: Path) -> dict:
    import yaml  # type: ignore

    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


def dump_yaml(path: Path, data: dict) -> None:
    import yaml  # type: ignore

    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )


def toggle_sla(data: dict) -> None:
    """Alterna falha do REQ-003 para mostrar atualização ao reexecutar."""
    tests = data.get("tests") or []
    for t in tests:
        if t.get("id") == "int-sla":
            t["status"] = "pass" if t.get("status") == "fail" else "fail"
            if t["status"] == "fail":
                t["message"] = "p95=240ms (limite 200ms)"
            else:
                t["message"] = None
            break
    layers = data.setdefault("layers", {})
    integ = layers.setdefault("integration", {})
    integ["failed"] = 1 if any(t.get("id") == "int-sla" and t.get("status") == "fail" for t in tests) else 0
    integ["passed"] = 2 if integ["failed"] else 3
    integ["status"] = "fail" if integ["failed"] else "pass"
    data["overall"] = "partial" if integ["failed"] else "pass"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--demo-root", type=Path, required=True)
    args = p.parse_args()
    manual = args.demo_root / "quality-runs" / "manual.yaml"
    if not manual.is_file():
        print(f"ERRO: {manual} ausente", file=sys.stderr)
        return 1
    data = load_yaml(manual)
    data["run_at"] = datetime.now(timezone.utc).astimezone().isoformat()
    data["ci_job"] = "demo-local-run"
    toggle_sla(data)
    dump_yaml(manual, data)
    print(f"OK: execução simulada → {manual}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
