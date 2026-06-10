#!/usr/bin/env python3
"""Export static HTML executive summary from process-metrics JSON."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_JSON = ROOT / "docs/meta/process-metrics/process-metrics.data.json"
DEFAULT_OUT = ROOT / "docs/meta/process-metrics/process-report.html"
DEMO_JSON = ROOT / "examples/process-metrics-demo/process-metrics/process-metrics.data.json"
DEMO_OUT = ROOT / "examples/process-metrics-demo/process-metrics/process-report.html"


def fmt_date(iso: str | None) -> str:
    if not iso:
        return "—"
    return iso[:10] if "T" in iso else iso


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--demo", action="store_true")
    p.add_argument("--json", type=Path)
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    json_path = args.json or (DEMO_JSON if args.demo else DEFAULT_JSON)
    out_path = args.out or (DEMO_OUT if args.demo else DEFAULT_OUT)

    if not json_path.exists():
        print(f"ERRO: JSON ausente ({json_path})", flush=True)
        return 1

    data = json.loads(json_path.read_text(encoding="utf-8"))
    rep = data.get("report") or {}
    agg = data.get("aggregates") or {}
    proj = agg.get("project") or {}
    fc = data.get("forecasts") or {}
    gates = data.get("gates") or {}
    title = html.escape(rep.get("project_name") or "Projeto")
    mvp = fmt_date(fc.get("project_delivery_forecast_date"))
    enabled = fc.get("enabled")
    human_h = round((proj.get("human_active_seconds") or 0) / 3600, 1)
    ai_h = round((proj.get("ai_execution_seconds") or 0) / 3600, 1)

    forecast_block = (
        f"<p><strong>Conclusão prevista do backlog (est.):</strong> {html.escape(mvp)}</p>"
        if enabled and mvp != "—"
        else "<p><em>Previsões desabilitadas até <code>mvp_planning.status: complete</code> e cards pendentes.</em></p>"
    )

    body = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8"/>
  <title>Relatório — {title}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; }}
    h1 {{ font-size: 1.4rem; }}
    .muted {{ color: #64748b; font-size: 0.9rem; }}
    .box {{ background: #f1f5f9; padding: 1rem; border-radius: 8px; margin: 1rem 0; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <p class="muted">{html.escape(rep.get("subtitle") or "")}</p>
  <div class="box">
    <p><strong>Humano ativo (projeto):</strong> {human_h} h</p>
    <p><strong>IA (est.):</strong> {ai_h} h</p>
    <p><strong>Calendário:</strong> {agg.get("calendar_project_span_days") or "—"} dias</p>
    {forecast_block}
  </div>
  <p class="muted">Planejamento MVP: {html.escape(str(gates.get("mvp_planning_status") or "—"))} ·
  Front: {html.escape(str(gates.get("has_frontend")))}</p>
  <p class="muted">{html.escape(fc.get("disclaimer_short") or rep.get("forecast_disclaimer_short") or "")}</p>
</body>
</html>
"""
    out_path.write_text(body, encoding="utf-8")
    print(f"OK: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
