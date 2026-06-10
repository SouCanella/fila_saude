#!/usr/bin/env python3
"""YAML process-timeline → JSON + aggregates for dashboard."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ACTIVITY_LABELS = {
    "ideation": "Idealização",
    "discovery": "Descoberta",
    "planning_review": "Planejamento",
    "bootstrap": "Bootstrap",
    "design_mock": "Mocks HTML",
    "design_approved": "Aprovação visual",
    "architecture_baseline": "Arquitetura acordada",
    "spec_refinement": "Refino specs",
    "implementation": "Implementação",
    "phase_retro": "Retro",
    "refinement": "Refinamento",
    "phase_delivery_start": "Início fase",
    "phase_delivery_end": "Fim fase",
    "mvp_planning_start": "Início planejamento MVP",
    "mvp_planning_end": "Fim planejamento MVP",
    "unknown": "A revisar",
}

ROOT = Path(__file__).resolve().parent.parent
YAML_PATH = ROOT / "docs/meta/process-timeline.yaml"
JSON_PATH = ROOT / "docs/meta/process-metrics/process-metrics.data.json"
CONFIG_PATH = ROOT / "project.config.yaml"
CARDS_BACKLOG = ROOT / "docs/planning/cards-backlog.md"
MVP_PHASES = ROOT / "docs/planning/mvp-phases.md"
CARDS_DIR = ROOT / "docs/tracking/cards"

_CTX: dict[str, Path] = {
    "yaml": YAML_PATH,
    "json": JSON_PATH,
    "config": CONFIG_PATH,
    "cards_backlog": CARDS_BACKLOG,
    "mvp_phases": MVP_PHASES,
    "cards_dir": CARDS_DIR,
}


def set_paths(
    *,
    yaml: Path | None = None,
    json: Path | None = None,
    config: Path | None = None,
    cards_backlog: Path | None = None,
    mvp_phases: Path | None = None,
    cards_dir: Path | None = None,
) -> None:
    if yaml:
        _CTX["yaml"] = yaml
    if json:
        _CTX["json"] = json
    if config:
        _CTX["config"] = config
    if cards_backlog:
        _CTX["cards_backlog"] = cards_backlog
    if mvp_phases:
        _CTX["mvp_phases"] = mvp_phases
    if cards_dir:
        _CTX["cards_dir"] = cards_dir

FORECAST_DISCLAIMER_SHORT = (
    "Datas em roxo/tracejado = projeção estatística (médias históricas), "
    "não data de negócio nem SLA."
)
FORECAST_DISCLAIMER_LONG = (
    "As barras e eventos «previstos» são calculados por um modelo interno do método Modelo: "
    "média de esforço por card/fase já concluídos, encadeamento a partir do último evento "
    "registrado e razão calendário/esforço observada nos marcos. "
    "Não substituem planejamento comercial, compromisso com cliente ou datas em contrato."
)


def load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore
    except ImportError:
        print(
            "ERRO: PyYAML não instalado. Use: pip install pyyaml",
            file=sys.stderr,
        )
        sys.exit(1)
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        data = {}
    return data


def load_project_config() -> dict:
    try:
        import yaml  # type: ignore
    except ImportError:
        return {}
    path = _CTX["config"]
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return cfg if isinstance(cfg, dict) else {}


def load_config_idle_hours() -> float:
    pm = load_project_config().get("process_metrics") or {}
    return float(pm.get("idle_threshold_hours") or 4)


def load_config_gates() -> dict:
    cfg = load_project_config()
    project = cfg.get("project") or {}
    return {
        "discovery_status": (cfg.get("discovery") or {}).get("status"),
        "mvp_planning_status": (cfg.get("mvp_planning") or {}).get("status"),
        "bootstrap_status": (cfg.get("bootstrap") or {}).get("status"),
        "design_status": (cfg.get("design") or {}).get("status"),
        "has_frontend": project.get("has_frontend"),
        "has_backend": project.get("has_backend"),
        "project_name": project.get("name"),
    }


def empty_forecasts(reason: str) -> dict:
    return {
        "enabled": False,
        "disabled_reason": reason,
        "methodology": (
            "Projeções estatísticas disponíveis após "
            "`mvp_planning.status: complete` e backlog com cards pendentes."
        ),
        "disclaimer_short": FORECAST_DISCLAIMER_SHORT,
        "disclaimer_long": FORECAST_DISCLAIMER_LONG,
        "date_kind_forecast": "statistical_projection",
        "phases": [],
        "cards": [],
        "delivery_schedule": [],
        "project_delivery_forecast_at": None,
        "project_delivery_forecast_date": None,
    }


def forecasts_are_enabled(gates: dict, backlog: list[dict]) -> tuple[bool, str]:
    if gates.get("mvp_planning_status") != "complete":
        return False, "mvp_planning_incomplete"
    if not backlog:
        return False, "no_backlog"
    pending = [c for c in backlog if c.get("status") not in ("done", "cancelled")]
    if not pending:
        return False, "no_pending_cards"
    return True, "ok"


def parse_iso(s: str | None) -> datetime | None:
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ):
        try:
            if fmt.endswith("%z") and s[-6] in "+-":
                return datetime.strptime(s, fmt)
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def sum_rounds(rounds: list, phase: str | None = None, activity: str | None = None) -> dict:
    human = ai = idle = 0
    for r in rounds:
        if not isinstance(r, dict):
            continue
        if phase and r.get("phase") != phase:
            continue
        if activity and r.get("activity") != activity:
            continue
        human += int(r.get("human_active_seconds") or 0)
        ai += int(r.get("ai_execution_seconds") or 0)
        ib = int(r.get("idle_before_seconds") or 0)
        idle += ib
    return {"human_active_seconds": human, "ai_execution_seconds": ai, "idle_seconds": idle}


def effort_seconds(block: dict) -> int:
    return (
        int(block.get("human_active_seconds") or 0)
        + int(block.get("ai_execution_seconds") or 0)
        + int(block.get("idle_seconds") or 0)
    )


def seconds_to_days(seconds: int | float) -> float:
    return round(float(seconds) / 86400, 2)


def iso_to_day_key(s: str | None) -> str | None:
    dt = parse_iso(s)
    if not dt:
        return None
    return dt.date().isoformat()


def compute_by_day(rounds: list) -> list[dict]:
    buckets: dict[str, dict] = {}
    for r in rounds:
        if not isinstance(r, dict):
            continue
        dk = iso_to_day_key(r.get("at"))
        if not dk:
            continue
        if dk not in buckets:
            buckets[dk] = {
                "date": dk,
                "human_active_seconds": 0,
                "ai_execution_seconds": 0,
                "idle_seconds": 0,
                "rounds_count": 0,
            }
        buckets[dk]["human_active_seconds"] += int(r.get("human_active_seconds") or 0)
        buckets[dk]["ai_execution_seconds"] += int(r.get("ai_execution_seconds") or 0)
        buckets[dk]["idle_seconds"] += int(r.get("idle_before_seconds") or 0)
        buckets[dk]["rounds_count"] += 1
    result = []
    for dk in sorted(buckets.keys()):
        b = buckets[dk]
        total = effort_seconds(b)
        result.append(
            {
                **b,
                "total_seconds": total,
                "total_days": seconds_to_days(total),
            }
        )
    return result


def project_calendar_span_days(
    project_started_at: str | None, rounds: list, milestones: list
) -> int | None:
    stamps = []
    if project_started_at:
        dt = parse_iso(project_started_at)
        if dt:
            stamps.append(dt)
    for r in rounds:
        if isinstance(r, dict):
            dt = parse_iso(r.get("at"))
            if dt:
                stamps.append(dt)
    for m in milestones:
        if not isinstance(m, dict):
            continue
        for key in ("started_at", "ended_at"):
            dt = parse_iso(m.get(key))
            if dt:
                stamps.append(dt)
    if len(stamps) < 2:
        return 1 if stamps else None
    delta = max(stamps) - min(stamps)
    return max(1, int(delta.total_seconds() // 86400) + 1)


def parse_card_frontmatter(card_id: str) -> dict:
    path = _CTX["cards_dir"] / f"{card_id}.md"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end < 0:
        return {}
    try:
        import yaml  # type: ignore

        meta = yaml.safe_load(text[3:end]) or {}
    except Exception:
        return {}
    if not isinstance(meta, dict):
        return {}
    return {
        "opened_at": meta.get("opened_at"),
        "done_at": meta.get("done_at"),
        "status": meta.get("status"),
    }


def parse_cards_backlog() -> list[dict]:
    path = _CTX["cards_backlog"]
    if not path.exists():
        return []
    cards = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "CARD-" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 7:
            continue
        card_id = parts[1]
        if not card_id.startswith("CARD-"):
            continue
        extra = parse_card_frontmatter(card_id)
        status = (extra.get("status") or parts[5] or "open").lower()
        cards.append(
            {
                "card_id": card_id,
                "phase": parts[2] if parts[2].startswith("FASE-") else None,
                "title": parts[3] or card_id,
                "status": status,
                "opened_at": extra.get("opened_at"),
                "done_at": extra.get("done_at"),
            }
        )
    return cards


def parse_mvp_phases() -> list[str]:
    path = _CTX["mvp_phases"]
    if not path.exists():
        return []
    phases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        for token in line.split():
            if token.startswith("FASE-") and token not in phases:
                phases.append(token)
    return phases


def phases_completed(milestones: list) -> set[str]:
    done = set()
    for m in milestones:
        if not isinstance(m, dict):
            continue
        if m.get("activity") == "phase_delivery_end" and m.get("ended_at") and m.get("phase"):
            done.add(m["phase"])
    return done


def card_effort_from_rounds(rounds: list) -> dict[str, dict]:
    by_card: dict[str, dict] = {}
    for r in rounds:
        if not isinstance(r, dict):
            continue
        cid = r.get("card_id")
        if not cid:
            continue
        if cid not in by_card:
            by_card[cid] = {
                "human_active_seconds": 0,
                "ai_execution_seconds": 0,
                "idle_seconds": 0,
                "phase": r.get("phase"),
                "rounds_count": 0,
            }
        by_card[cid]["human_active_seconds"] += int(r.get("human_active_seconds") or 0)
        by_card[cid]["ai_execution_seconds"] += int(r.get("ai_execution_seconds") or 0)
        by_card[cid]["idle_seconds"] += int(r.get("idle_before_seconds") or 0)
        by_card[cid]["rounds_count"] += 1
        if r.get("phase"):
            by_card[cid]["phase"] = r.get("phase")
    return by_card


def confidence_label(samples: int) -> str:
    if samples >= 2:
        return "alta"
    if samples == 1:
        return "media"
    return "baixa"


def compute_forecasts(data: dict, aggregates: dict, gates: dict | None = None) -> dict:
    gates = gates or load_config_gates()
    backlog = parse_cards_backlog()
    ok, reason = forecasts_are_enabled(gates, backlog)
    if not ok:
        return empty_forecasts(reason)

    rounds = data.get("rounds") or []
    milestones = data.get("milestones") or []
    by_phase = aggregates.get("by_phase") or {}
    backlog = parse_cards_backlog()
    mvp_phases = parse_mvp_phases() or sorted(
        {c["phase"] for c in backlog if c.get("phase")}
    )
    completed = phases_completed(milestones)
    card_hist = card_effort_from_rounds(rounds)

    product_phases = sorted(
        {p for p in by_phase if p and p.startswith("FASE-")},
        key=lambda x: int(x.split("-")[1]) if "-" in x else 0,
    )
    completed_product = [p for p in product_phases if p in completed]
    phase_efforts = [effort_seconds(by_phase[p]) for p in completed_product]
    avg_phase_effort = (
        int(sum(phase_efforts) / len(phase_efforts)) if phase_efforts else 0
    )

    active_sum = sum(
        int(by_phase[p].get("human_active_seconds") or 0)
        + int(by_phase[p].get("ai_execution_seconds") or 0)
        for p in completed_product
    ) or 1
    calendar_product = 0
    for m in milestones:
        if not isinstance(m, dict):
            continue
        if m.get("phase") in completed_product and m.get("activity") == "phase_delivery_end":
            s, e = parse_iso(m.get("started_at")), parse_iso(m.get("ended_at"))
            if s and e:
                calendar_product += max(0, int((e - s).total_seconds()))
    calendar_ratio = calendar_product / active_sum if active_sum else 1.2

    cards_by_phase: dict[str, list[int]] = {}
    for cid, block in card_hist.items():
        ph = block.get("phase") or "unknown"
        cards_by_phase.setdefault(ph, []).append(effort_seconds(block))

    global_card_avg = 0
    all_card_efforts = [effort_seconds(b) for b in card_hist.values()]
    if all_card_efforts:
        global_card_avg = int(sum(all_card_efforts) / len(all_card_efforts))

    phase_forecasts = []
    for ph in mvp_phases:
        if not ph.startswith("FASE-"):
            continue
        if ph in completed:
            continue
        pending_cards = [c for c in backlog if c.get("phase") == ph and c.get("status") != "done"]
        n_cards = len(pending_cards) or max(1, len(cards_by_phase.get(ph, [])))
        if cards_by_phase.get(ph):
            est = int(sum(cards_by_phase[ph]) / len(cards_by_phase[ph]) * n_cards)
        elif avg_phase_effort:
            est = avg_phase_effort
        else:
            est = global_card_avg * n_cards if global_card_avg else 0
        est_active = est
        est_calendar = int(est_active * calendar_ratio)
        phase_forecasts.append(
            {
                "phase": ph,
                "status": "pendente",
                "pending_cards_count": len(pending_cards),
                "estimated_active_seconds": est_active,
                "estimated_calendar_seconds": est_calendar,
                "estimated_active_days": seconds_to_days(est_active),
                "estimated_calendar_days": seconds_to_days(est_calendar),
                "estimated_human_seconds": int(est_active * 0.55),
                "estimated_ai_seconds": int(est_active * 0.30),
                "estimated_idle_seconds": int(est_active * 0.15),
                "based_on_completed_phases": len(completed_product),
                "confidence": confidence_label(len(completed_product)),
            }
        )

    card_forecasts = []
    for c in backlog:
        if c.get("status") == "done":
            continue
        ph = c.get("phase") or "unknown"
        hist = cards_by_phase.get(ph, [])
        if hist:
            est = int(sum(hist) / len(hist))
            conf = confidence_label(len(hist))
        elif global_card_avg:
            est = global_card_avg
            conf = confidence_label(len(all_card_efforts))
        else:
            est = 0
            conf = "baixa"
        est_cal = int(est * calendar_ratio)
        card_forecasts.append(
            {
                "card_id": c["card_id"],
                "phase": ph,
                "title": c.get("title"),
                "status": c.get("status"),
                "estimated_active_seconds": est,
                "estimated_calendar_seconds": est_cal,
                "estimated_active_days": seconds_to_days(est),
                "estimated_calendar_days": seconds_to_days(est_cal),
                "confidence": conf,
            }
        )

    return {
        "enabled": True,
        "disabled_reason": None,
        "methodology": (
            "Modelo estatístico: médias de esforço (rodadas) em fases/cards concluídos; "
            "projeção de calendário = esforço ativo × razão observada nos marcos. "
            "Não são datas de negócio."
        ),
        "disclaimer_short": FORECAST_DISCLAIMER_SHORT,
        "disclaimer_long": FORECAST_DISCLAIMER_LONG,
        "date_kind_forecast": "statistical_projection",
        "date_kind_actual_card": "tracked_delivery",
        "calendar_ratio": round(calendar_ratio, 2),
        "completed_phases": sorted(completed),
        "avg_completed_phase_seconds": avg_phase_effort,
        "avg_card_seconds_global": global_card_avg,
        "phases": phase_forecasts,
        "cards": card_forecasts,
    }


def compute_aggregates(data: dict, idle_threshold_hours: float) -> dict:
    rounds = data.get("rounds") or []
    milestones = data.get("milestones") or []
    sessions = data.get("sessions") or []

    phases = set()
    activities = set()
    for r in rounds:
        if isinstance(r, dict):
            if r.get("phase"):
                phases.add(r["phase"])
            if r.get("activity"):
                activities.add(r["activity"])
    for m in milestones:
        if isinstance(m, dict) and m.get("phase"):
            phases.add(m["phase"])
    for s in sessions:
        if isinstance(s, dict) and s.get("phase"):
            phases.add(s["phase"])

    by_phase = {p: sum_rounds(rounds, phase=p) for p in sorted(phases)}
    by_activity = {a: sum_rounds(rounds, activity=a) for a in sorted(activities)}
    project = sum_rounds(rounds)

    calendar_seconds = 0
    for m in milestones:
        if not isinstance(m, dict):
            continue
        start = parse_iso(m.get("started_at"))
        end = parse_iso(m.get("ended_at"))
        if start and end:
            calendar_seconds += max(0, int((end - start).total_seconds()))

    effort_total = effort_seconds(project)
    by_day = compute_by_day(rounds)

    activity_averages = compute_activity_averages(rounds)

    return {
        "idle_threshold_hours": idle_threshold_hours,
        "project": project,
        "by_phase": by_phase,
        "by_activity": by_activity,
        "by_day": by_day,
        "activity_averages": activity_averages,
        "calendar_from_milestones_seconds": calendar_seconds,
        "calendar_from_milestones_days": seconds_to_days(calendar_seconds),
        "project_effort_days": seconds_to_days(effort_total),
        "rounds_needing_review": sum(
            1 for r in rounds if isinstance(r, dict) and r.get("needs_review")
        ),
    }


def compute_activity_averages(rounds: list) -> list[dict]:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for r in rounds:
        if not isinstance(r, dict):
            continue
        act = r.get("activity") or "unknown"
        buckets[act].append(
            {
                "human": int(r.get("human_active_seconds") or 0),
                "ai": int(r.get("ai_execution_seconds") or 0),
                "idle": int(r.get("idle_before_seconds") or 0),
            }
        )
    out = []
    for act in sorted(buckets.keys()):
        items = buckets[act]
        n = len(items)
        if n == 0:
            continue
        avg_h = sum(x["human"] for x in items) / n
        avg_ai = sum(x["ai"] for x in items) / n
        avg_idle = sum(x["idle"] for x in items) / n
        avg_total = avg_h + avg_ai + avg_idle
        out.append(
            {
                "activity": act,
                "label": ACTIVITY_LABELS.get(act, act),
                "rounds_count": n,
                "avg_human_seconds": int(avg_h),
                "avg_ai_seconds": int(avg_ai),
                "avg_idle_seconds": int(avg_idle),
                "avg_total_seconds": int(avg_total),
                "avg_total_days": seconds_to_days(avg_total),
            }
        )
    return out


def dt_to_iso(dt: datetime | None) -> str | None:
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def latest_timestamp(data: dict, forecasts: dict) -> datetime | None:
    stamps: list[datetime] = []
    for r in data.get("rounds") or []:
        if isinstance(r, dict):
            dt = parse_iso(r.get("at"))
            if dt:
                stamps.append(dt)
    for m in data.get("milestones") or []:
        if not isinstance(m, dict):
            continue
        for k in ("started_at", "ended_at"):
            dt = parse_iso(m.get(k))
            if dt:
                stamps.append(dt)
    if not stamps:
        return datetime.now(timezone.utc)
    return max(stamps)


def compute_gantt(data: dict, forecasts: dict, backlog: list[dict]) -> dict:
    rounds = data.get("rounds") or []
    milestones = data.get("milestones") or []
    tasks: list[dict] = []
    forecast_by_card = {c["card_id"]: c for c in forecasts.get("cards") or []}

    for m in milestones:
        if not isinstance(m, dict):
            continue
        start = parse_iso(m.get("started_at"))
        end = parse_iso(m.get("ended_at"))
        if not start:
            continue
        act = m.get("activity") or "milestone"
        tasks.append(
            {
                "id": m.get("id") or act,
                "label": ACTIVITY_LABELS.get(act, act),
                "group": m.get("phase") or "SETUP",
                "kind": "milestone",
                "status": "done" if end else "active",
                "actual_start": dt_to_iso(start),
                "actual_end": dt_to_iso(end),
                "planned_start": dt_to_iso(start),
                "planned_end": dt_to_iso(end or start),
            }
        )

    card_times: dict[str, list[datetime]] = defaultdict(list)
    for r in rounds:
        if not isinstance(r, dict) or not r.get("card_id"):
            continue
        dt = parse_iso(r.get("at"))
        if dt:
            card_times[r["card_id"]].append(dt)

    cursor = latest_timestamp(data, forecasts)
    phase_cards: dict[str, list] = defaultdict(list)

    for card in backlog:
        cid = card["card_id"]
        phase = card.get("phase") or "—"
        title = card.get("title") or cid
        status = card.get("status") or "open"
        label = f"{cid} — {title}"

        opened = parse_iso(card.get("opened_at"))
        done_at = parse_iso(card.get("done_at"))

        if status == "done":
            start = opened or (min(card_times[cid]) if card_times.get(cid) else None)
            end = done_at or (max(card_times[cid]) if card_times.get(cid) else None)
            if start and end:
                date_source = "card_dates" if (opened and done_at) else "rounds_fallback"
                tasks.append(
                    {
                        "id": cid,
                        "label": label,
                        "group": phase,
                        "kind": "card",
                        "status": "done",
                        "date_source": date_source,
                        "planned_date_kind": "tracked_delivery",
                        "actual_start": dt_to_iso(start),
                        "actual_end": dt_to_iso(end),
                        "planned_start": dt_to_iso(start),
                        "planned_end": dt_to_iso(end),
                    }
                )
                cursor = max(cursor, end)
        elif status == "in_progress" and opened:
            end = done_at or (
                max(card_times[cid]) if card_times.get(cid) else datetime.now(timezone.utc)
            )
            tasks.append(
                {
                    "id": cid,
                    "label": label,
                    "group": phase,
                    "kind": "card",
                    "status": "active",
                    "date_source": "card_opened_at",
                    "planned_date_kind": "tracked_delivery",
                    "actual_start": dt_to_iso(opened),
                    "actual_end": dt_to_iso(end),
                    "planned_start": dt_to_iso(opened),
                    "planned_end": dt_to_iso(end),
                }
            )
            if isinstance(end, datetime):
                cursor = max(cursor, end)
        elif status != "done" and forecasts.get("enabled"):
            fc = forecast_by_card.get(cid)
            est_sec = int(
                (fc or {}).get("estimated_calendar_seconds")
                or forecasts.get("avg_card_seconds_global")
                or 86400
            )
            start = cursor
            end = cursor + timedelta(seconds=est_sec)
            cursor = end + timedelta(hours=4)
            tasks.append(
                {
                    "id": cid,
                    "label": label,
                    "group": phase,
                    "kind": "card",
                    "status": "forecast",
                    "date_source": "statistical_projection",
                    "planned_date_kind": "statistical_projection",
                    "actual_start": None,
                    "actual_end": None,
                    "planned_start": dt_to_iso(start),
                    "planned_end": dt_to_iso(end),
                }
            )
        phase_cards[phase].append(cid)

    if forecasts.get("enabled"):
        for pf in forecasts.get("phases") or []:
            ph = pf.get("phase")
            if not ph:
                continue
            est = int(pf.get("estimated_calendar_seconds") or 0)
            start = cursor
            end = cursor + timedelta(seconds=est) if est else cursor + timedelta(days=7)
            tasks.append(
                {
                    "id": f"forecast-{ph}",
                    "label": f"{ph} (projeção estatística)",
                    "group": ph,
                    "kind": "phase",
                    "status": "forecast",
                    "date_source": "statistical_projection",
                    "planned_date_kind": "statistical_projection",
                    "actual_start": None,
                    "actual_end": None,
                    "planned_start": dt_to_iso(start),
                    "planned_end": dt_to_iso(end),
                }
            )
            cursor = end

    tasks.sort(key=lambda t: (t.get("group") or "", t.get("planned_start") or ""))

    range_start = None
    range_end = None
    for t in tasks:
        for key in ("actual_start", "actual_end", "planned_start", "planned_end"):
            dt = parse_iso(t.get(key))
            if not dt:
                continue
            if range_start is None or dt < range_start:
                range_start = dt
            if range_end is None or dt > range_end:
                range_end = dt
    if range_start and range_end:
        pad = timedelta(days=2)
        range_start -= pad
        range_end += pad
    else:
        # Sem tarefas: intervalo fixo (build reproduzível no CI / make ci)
        range_start = None
        range_end = None

    return {
        "range_start": dt_to_iso(range_start),
        "range_end": dt_to_iso(range_end),
        "tasks": tasks,
    }


def enrich_forecasts_delivery_dates(forecasts: dict, gantt: dict) -> dict:
    """Align forecast cards/phases with Gantt planned dates (statistical projection)."""
    tasks = gantt.get("tasks") or []
    by_id = {t.get("id"): t for t in tasks if isinstance(t, dict) and t.get("id")}

    for card_fc in forecasts.get("cards") or []:
        if not isinstance(card_fc, dict):
            continue
        task = by_id.get(card_fc.get("card_id"))
        if not task or not task.get("planned_end"):
            continue
        card_fc["forecast_delivery_start_at"] = task.get("planned_start")
        card_fc["forecast_delivery_end_at"] = task.get("planned_end")
        card_fc["forecast_delivery_date"] = iso_to_day_key(task["planned_end"])

    for phase_fc in forecasts.get("phases") or []:
        if not isinstance(phase_fc, dict):
            continue
        phase = phase_fc.get("phase")
        task = by_id.get(f"forecast-{phase}") if phase else None
        if not task or not task.get("planned_end"):
            continue
        phase_fc["forecast_delivery_start_at"] = task.get("planned_start")
        phase_fc["forecast_delivery_end_at"] = task.get("planned_end")
        phase_fc["forecast_delivery_date"] = iso_to_day_key(task["planned_end"])

    schedule: list[dict] = []
    max_end: datetime | None = None
    for task in tasks:
        if not isinstance(task, dict) or task.get("status") != "forecast":
            continue
        end_at = task.get("planned_end")
        start_at = task.get("planned_start")
        schedule.append(
            {
                "id": task.get("id"),
                "label": task.get("label"),
                "kind": task.get("kind"),
                "phase": task.get("group"),
                "forecast_start_at": start_at,
                "forecast_end_at": end_at,
                "forecast_delivery_date": iso_to_day_key(end_at),
                "date_kind": task.get("planned_date_kind") or "statistical_projection",
            }
        )
        dt = parse_iso(end_at)
        if dt and (max_end is None or dt > max_end):
            max_end = dt

    schedule.sort(key=lambda x: x.get("forecast_end_at") or "")
    forecasts["delivery_schedule"] = schedule
    if max_end:
        forecasts["project_delivery_forecast_at"] = dt_to_iso(max_end)
        forecasts["project_delivery_forecast_date"] = iso_to_day_key(dt_to_iso(max_end))
    else:
        forecasts["project_delivery_forecast_at"] = None
        forecasts["project_delivery_forecast_date"] = None
    return forecasts


def compute_calendar_events(gantt: dict, forecasts: dict) -> list[dict]:
    events: list[dict] = []
    seen: set[tuple] = set()

    def add(
        day: str | None,
        title: str,
        kind: str,
        phase: str,
        card_id: str | None,
        date_kind: str,
    ):
        if not day:
            return
        key = (day, title, kind)
        if key in seen:
            return
        seen.add(key)
        events.append(
            {
                "date": day,
                "title": title,
                "kind": kind,
                "date_kind": date_kind,
                "phase": phase,
                "card_id": card_id,
            }
        )

    for t in gantt.get("tasks") or []:
        phase = t.get("group") or ""
        if t.get("actual_end"):
            dk = t.get("planned_date_kind") or "tracked_delivery"
            add(
                iso_to_day_key(t["actual_end"]),
                f"✓ {t['label']}",
                "delivery_actual",
                phase,
                t["id"] if t.get("kind") == "card" else None,
                dk,
            )
        if t.get("planned_end") and t.get("status") == "forecast":
            add(
                iso_to_day_key(t["planned_end"]),
                f"→ {t['label']} (est.)",
                "delivery_forecast",
                phase,
                t["id"] if t.get("kind") == "card" else None,
                "statistical_projection",
            )
        elif t.get("planned_end") and t.get("status") == "done" and not t.get("actual_end"):
            add(
                iso_to_day_key(t["planned_end"]),
                t["label"],
                "delivery_actual",
                phase,
                None,
                "tracked_delivery",
            )

    events.sort(key=lambda e: e.get("date") or "")
    return events


def load_config_metrics() -> dict:
    return load_project_config().get("process_metrics") or {}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build process metrics JSON")
    p.add_argument("--yaml", type=Path, help="process-timeline.yaml path")
    p.add_argument("--json", type=Path, help="output JSON path")
    p.add_argument("--config", type=Path, help="project.config.yaml path")
    p.add_argument("--cards-backlog", type=Path, help="cards-backlog.md path")
    p.add_argument("--mvp-phases", type=Path, help="mvp-phases.md path")
    p.add_argument("--cards-dir", type=Path, help="cards MD directory")
    return p.parse_args()


def build_metrics() -> int:
    yaml_path = _CTX["yaml"]
    json_path = _CTX["json"]
    if not yaml_path.exists():
        print(f"AVISO: {yaml_path} ausente")
        return 0

    data = load_yaml(yaml_path)
    idle_h = load_config_idle_hours()
    pm = load_config_metrics()
    gates = load_config_gates()
    data["gates"] = gates
    data["project_started_at"] = pm.get("project_started_at")
    data["process_metrics_config"] = {
        "idle_threshold_hours": idle_h,
        "ai_minutes_per_round_default": pm.get("ai_minutes_per_round_default") or 3,
        "active_context": pm.get("active_context"),
    }
    data["aggregates"] = compute_aggregates(data, idle_h)
    data["aggregates"]["calendar_project_span_days"] = project_calendar_span_days(
        pm.get("project_started_at"), data.get("rounds") or [], data.get("milestones") or []
    )
    backlog = parse_cards_backlog()
    data["forecasts"] = compute_forecasts(data, data["aggregates"], gates)
    data["gantt"] = compute_gantt(data, data["forecasts"], backlog)
    if data["forecasts"].get("enabled"):
        data["forecasts"] = enrich_forecasts_delivery_dates(data["forecasts"], data["gantt"])
    data["calendar_events"] = compute_calendar_events(data["gantt"], data["forecasts"])
    data["planning"] = {
        "cards_backlog": backlog,
        "mvp_phases": parse_mvp_phases(),
    }
    project_name = gates.get("project_name") or "Projeto"
    data["report"] = {
        "title": "Relatório de engenharia do processo",
        "subtitle": "Ferramenta do método Modelo — observabilidade do fluxo SDD/TDD",
        "project_name": project_name,
        "forecast_disclaimer_short": FORECAST_DISCLAIMER_SHORT,
        "forecast_disclaimer_long": FORECAST_DISCLAIMER_LONG,
        "panel_path": "docs/meta/process-metrics/index.html",
        "coverage_note": (
            "Cobertura de testes do produto fica no CI (project.config → coverage), "
            "não neste painel de tempo de processo."
        ),
    }
    data["built_at"] = datetime.now().astimezone().isoformat()

    json_path.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"OK: {json_path}")
    return 0


def main() -> int:
    args = parse_args()
    set_paths(
        yaml=args.yaml,
        json=args.json,
        config=args.config,
        cards_backlog=args.cards_backlog,
        mvp_phases=args.mvp_phases,
        cards_dir=args.cards_dir,
    )
    return build_metrics()


if __name__ == "__main__":
    sys.exit(main())
