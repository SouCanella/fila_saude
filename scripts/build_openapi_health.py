#!/usr/bin/env python3
"""Valida openapi.yaml → openapi.data.json."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


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


def resolve_openapi_path(root: Path, cfg: dict) -> Path:
    openapi_cfg = cfg.get("openapi") or {}
    rel = openapi_cfg.get("path") or "docs/api/openapi.yaml"
    p = root / rel
    if p.exists():
        return p
    alt = root / "docs" / rel.removeprefix("docs/")
    return alt if alt.exists() else p


def validate_openapi_doc(doc: dict, cfg: dict, bootstrap_complete: bool) -> dict:
    contract_first = (cfg.get("openapi") or {}).get("contract_first", True)
    paths = doc.get("paths") or {}
    path_count = len(paths) if isinstance(paths, dict) else 0
    parseable = bool(doc.get("openapi") or doc.get("swagger"))
    stub = path_count == 0
    valid = parseable
    if contract_first and path_count == 0:
        valid = False
    return {
        "parseable": parseable,
        "path_count": path_count,
        "stub": stub,
        "valid": valid,
        "contract_first": contract_first,
        "bootstrap_complete": bootstrap_complete,
    }


def try_redocly(path: Path) -> dict | None:
    import os
    import shutil

    if os.environ.get("OPENAPI_REDOCLY", "") != "1":
        return None
    redocly = shutil.which("redocly")
    if not redocly:
        return None
    try:
        subprocess.run(
            [redocly, "lint", str(path)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return {"redocly_ran": True}
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None


def build_payload(root: Path, config_path: Path) -> dict:
    cfg = load_yaml(config_path)
    path = resolve_openapi_path(root, cfg)
    doc = load_yaml(path)
    bootstrap = (cfg.get("bootstrap") or {}).get("status") == "complete"
    report = validate_openapi_doc(doc, cfg, bootstrap)
    redocly = try_redocly(path) if path.exists() and report["parseable"] else None
    return {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "source": str(path.relative_to(root)) if path.is_relative_to(root) else str(path),
        "info": doc.get("info") or {},
        "report": {**report, **(redocly or {"redocly_ran": False})},
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
