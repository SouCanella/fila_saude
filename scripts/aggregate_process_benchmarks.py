#!/usr/bin/env python3
"""Aggregate benchmark snapshots into docs/meta/process-benchmarks/index.md."""
from __future__ import annotations

import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAP_DIR = ROOT / "docs/meta/process-benchmarks/snapshots"
OUT = ROOT / "docs/meta/process-benchmarks/index.md"


def median_or_none(values: list[float]) -> float | None:
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    return round(statistics.median(vals), 2)


def main() -> int:
    files = sorted(SNAP_DIR.glob("benchmark-*.json"))
    rows: list[dict] = []
    ratios: list[float] = []
    card_counts: list[int] = []
    phase_counts: list[int] = []

    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(data, dict):
            continue
        rows.append(data)
        if data.get("calendar_ratio") is not None:
            ratios.append(float(data["calendar_ratio"]))
        if data.get("card_count") is not None:
            card_counts.append(int(data["card_count"]))
        if data.get("phase_count") is not None:
            phase_counts.append(int(data["phase_count"]))

    lines = [
        "# Índice de benchmarks (gerado)",
        "",
        f"_Atualizado: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_ · "
        f"Fonte: `snapshots/benchmark-*.json` · Regenerar: `./scripts/aggregate-process-benchmarks.sh`",
        "",
        "## Faixas agregadas",
        "",
        "| Métrica | Mediana | Amostras |",
        "|---------|---------|----------|",
        f"| `calendar_ratio` | {median_or_none(ratios) or '—'} | {len(ratios)} |",
        f"| `card_count` | {median_or_none([float(x) for x in card_counts]) or '—'} | {len(card_counts)} |",
        f"| `phase_count` | {median_or_none([float(x) for x in phase_counts]) or '—'} | {len(phase_counts)} |",
        "",
        "> Projeções nos snapshots são **estatísticas**, não SLA. Ver disclaimers em cada JSON.",
        "",
    ]

    if rows:
        lines.extend(["## Snapshots", "", "| Arquivo | Stack | Cards | Fases | Ratio | MVP (est.) |", "|---------|-------|-------|-------|-------|------------|"])
        for path in files:
            try:
                d = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            stack = d.get("stack") or {}
            st = f"{stack.get('backend') or '—'}/{stack.get('frontend') or '—'}"
            lines.append(
                f"| `{path.name}` | {st} | {d.get('card_count', '—')} | "
                f"{d.get('phase_count', '—')} | {d.get('calendar_ratio', '—')} | "
                f"{d.get('project_delivery_forecast_date') or '—'} |"
            )
        lines.append("")
    else:
        lines.extend(
            [
                "_Nenhum snapshot ainda._ Exporte com `./scripts/export-process-benchmark.sh` após build das métricas.",
                "",
            ]
        )

    lines.append("Ver [README.md](README.md) e demo em [examples/process-metrics-demo](../../examples/process-metrics-demo/README.md).")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK: {OUT} ({len(rows)} snapshot(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
