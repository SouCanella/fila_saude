#!/usr/bin/env python3
"""Export anonymized process metrics snapshot for cross-project benchmarks."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "docs/meta/process-metrics/process-metrics.data.json"
CONFIG_PATH = ROOT / "project.config.yaml"
OUT_DIR = ROOT / "docs/meta/process-benchmarks/snapshots"


def load_config() -> dict:
    try:
        import yaml  # type: ignore
    except ImportError:
        return {}
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    stack = cfg.get("stack") or {}
    project = cfg.get("project") or {}
    return {
        "has_frontend": project.get("has_frontend"),
        "has_backend": project.get("has_backend"),
        "has_database": project.get("has_database"),
        "backend": stack.get("backend"),
        "frontend": stack.get("frontend"),
        "monorepo": stack.get("monorepo"),
        "mvp_planning_status": (cfg.get("mvp_planning") or {}).get("status"),
        "discovery_status": (cfg.get("discovery") or {}).get("status"),
        "bootstrap_status": (cfg.get("bootstrap") or {}).get("status"),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--json", type=Path, default=None, help="metrics JSON path")
    p.add_argument("--out", type=Path, default=None, help="output file (default: snapshots/benchmark-*.json)")
    return p.parse_args()


def main(args: argparse.Namespace | None = None) -> int:
    args = args or parse_args()
    json_path = args.json or Path(os.environ.get("PROCESS_METRICS_JSON", JSON_PATH))
    if not json_path.exists():
        print(f"ERRO: rode build das métricas primeiro ({json_path})", file=sys.stderr)
        return 1

    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)

    agg = data.get("aggregates") or {}
    fc = data.get("forecasts") or {}
    planning = data.get("planning") or {}
    backlog = planning.get("cards_backlog") or []
    phases = planning.get("mvp_phases") or []

    snapshot = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "stack": load_config(),
        "phase_count": len(phases),
        "card_count": len(backlog),
        "cards_done": sum(1 for c in backlog if c.get("status") == "done"),
        "rounds_count": len(data.get("rounds") or []),
        "rounds_needing_review": agg.get("rounds_needing_review"),
        "calendar_ratio": fc.get("calendar_ratio"),
        "project_delivery_forecast_date": fc.get("project_delivery_forecast_date"),
        "delivery_schedule_count": len(fc.get("delivery_schedule") or []),
        "avg_card_seconds_global": fc.get("avg_card_seconds_global"),
        "avg_completed_phase_seconds": fc.get("avg_completed_phase_seconds"),
        "activity_averages": agg.get("activity_averages"),
        "project_effort_days": agg.get("project_effort_days"),
        "calendar_project_span_days": agg.get("calendar_project_span_days"),
        "forecasts_disclaimer_short": fc.get("disclaimer_short")
        or (data.get("report") or {}).get("forecast_disclaimer_short"),
        "forecasts_disclaimer_long": fc.get("disclaimer_long")
        or (data.get("report") or {}).get("forecast_disclaimer_long"),
        "note": "Projeções exportadas são modelo estatístico — não datas de negócio.",
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%dT%H-%M")
    out = args.out or (OUT_DIR / f"benchmark-{stamp}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"OK: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
