#!/usr/bin/env python3
"""Agrega JSONs dos módulos + next_step → hub.data.json."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "scripts"))
from resolve_next_step import resolve_next_step  # noqa: E402


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def build_overview(
    root: Path,
    data_dir: Path,
    config_path: Path | None = None,
    cards_dir: Path | None = None,
    specs_dir: Path | None = None,
) -> dict:
    process = load_json(data_dir / "process.data.json")
    quality = load_json(data_dir / "quality.data.json")
    security = load_json(data_dir / "security.data.json")
    a11y = load_json(data_dir / "a11y.data.json")
    design = load_json(data_dir / "design.data.json")

    q_an = quality.get("analytics") or {}
    q_rep = quality.get("report") or {}
    p_agg = process.get("aggregates") or {}
    sec_rep = security.get("report") or {}
    a11y_rep = a11y.get("report") or {}
    des_rep = design.get("report") or {}

    delivery = load_json(data_dir / "delivery.data.json")
    learning = load_json(data_dir / "learning.data.json")
    journey = load_json(data_dir / "journey.data.json")
    tech_debt = load_json(data_dir / "tech_debt.data.json")
    openapi = load_json(data_dir / "openapi.data.json")
    release = load_json(data_dir / "release.data.json")
    del_rep = delivery.get("report") or {}
    learn_rep = learning.get("report") or {}
    bench = learning.get("benchmarks") or {}
    j_life = journey.get("lifecycle") or {}
    j_rep = journey.get("report") or {}
    td_rep = tech_debt.get("report") or {}
    oai_rep = openapi.get("report") or {}
    rel_rep = release.get("report") or {}
    compliance_ok = sec_rep.get("compliance_ok")
    if compliance_ok is None:
        compliance_ok = (security.get("compliance") or {}).get("ok", False)

    cfg_path = config_path or root / "project.config.yaml"
    cfg_data = load_json_path_config(cfg_path)
    template_cfg = cfg_data.get("template") or {}
    next_step = resolve_next_step(root, config_path, cards_dir, specs_dir, data_dir)

    return {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "project_name": cfg_data.get("project", {}).get("name"),
        "template": {
            "is_upstream": template_cfg.get("is_upstream"),
            "sibling_spawn_required": template_cfg.get("sibling_spawn_required"),
            "upstream_dev_mode": template_cfg.get("upstream_dev_mode"),
        },
        "modules": {
            "process": bool(process),
            "quality": bool(quality),
            "security": bool(security),
            "accessibility": bool(a11y),
            "design": bool(design),
            "delivery": bool(delivery.get("entries")),
            "learning": bool(learning.get("retrospectives") or bench.get("snapshot_count")),
            "journey": bool(journey.get("lifecycle")),
        },
        "kpis": {
            "health_score": q_an.get("health_score"),
            "req_fully_green_pct": q_rep.get("req_fully_green_pct"),
            "quality_gaps": q_rep.get("gap_count", 0),
            "forecast_days_remaining": p_agg.get("forecast_days_remaining"),
            "security_gaps": sec_rep.get("gap_count", 0),
            "a11y_checklist_pct": a11y_rep.get("checklist_pct"),
            "design_ready": des_rep.get("ready_for_ui_impl", False),
            "delivery_total": del_rep.get("total", 0),
            "delivery_completed": del_rep.get("completed", 0),
            "retro_pending": learn_rep.get("retro_pending", 0),
            "benchmark_snapshots": bench.get("snapshot_count", 0),
            "phases_complete": j_life.get("phases_complete", 0),
            "phases_total": j_life.get("phases_total", 0),
            "current_phase_id": j_life.get("current_phase_id"),
            "activity_count": j_rep.get("activity_count", 0),
            "tech_debt_critical": td_rep.get("critical_open_count", 0),
            "openapi_valid": oai_rep.get("valid", False),
            "openapi_path_count": oai_rep.get("path_count", 0),
            "compliance_ok": compliance_ok,
            "last_release": rel_rep.get("last_tag"),
        },
        "delivery": delivery,
        "learning": learning,
        "journey": journey,
        "tech_debt": tech_debt,
        "openapi": openapi,
        "release": release,
        "next_step": next_step,
    }


def load_json_path_config(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        import yaml  # type: ignore

        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--data-dir", type=Path, required=True)
    p.add_argument("--config", type=Path)
    p.add_argument("--cards-dir", type=Path)
    p.add_argument("--specs-dir", type=Path)
    p.add_argument("--json", type=Path, required=True)
    args = p.parse_args()
    root = args.root.resolve()
    overview = build_overview(root, args.data_dir, args.config, args.cards_dir, args.specs_dir)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(overview, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
