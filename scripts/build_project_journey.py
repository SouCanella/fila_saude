#!/usr/bin/env python3
"""Project journey — fases, entregas enriquecidas, activity feed → journey.data.json."""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "scripts"))
from build_delivery_history import parse_delivery_log, resolve_delivery_log  # noqa: E402
from modelo_ids import BACKLOG_REQ_ROW_RE  # noqa: E402


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


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def load_frontmatter(path: Path) -> dict:
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
        return meta if isinstance(meta, dict) else {}
    except Exception:
        return {}


def resolve_path(root: Path, rel: str) -> Path:
    p = root / rel
    if p.exists():
        return p
    alt = root / "docs" / rel.removeprefix("docs/")
    return alt if alt.exists() else p


def load_artifact_manifest(root: Path) -> dict:
    for candidate in (
        root / "docs/meta/project-artifacts.yaml",
        ROOT / "docs/meta/project-artifacts.yaml",
    ):
        if candidate.exists():
            return load_yaml(candidate)
    return {}


def expand_manifest_paths(root: Path, manifest: dict) -> list[dict]:
    items: list[dict] = []
    for art in manifest.get("artifacts") or []:
        path = art.get("path")
        if not path:
            continue
        full = resolve_path(root, path)
        items.append({**art, "path": path, "resolved": full})
    for glob_def in manifest.get("glob_patterns") or []:
        pattern = glob_def.get("pattern", "")
        base = pattern.split("*")[0].rstrip("/")
        search_root = resolve_path(root, base) if base else root
        if not search_root.exists():
            search_root = root / base if base else root
        if search_root.is_file():
            candidates = [search_root]
        elif search_root.is_dir():
            candidates = list(search_root.rglob("*"))
        else:
            glob_from = root / pattern
            parent = glob_from.parent
            name = glob_from.name
            candidates = list(parent.glob(name)) if parent.exists() else []
        for full in candidates:
            if not full.is_file():
                continue
            rel = str(full.relative_to(root)) if full.is_relative_to(root) else str(full)
            if not fnmatch.fnmatch(rel, pattern) and not fnmatch.fnmatch(full.name, pattern.split("/")[-1]):
                continue
            items.append(
                {
                    "path": rel,
                    "resolved": full,
                    "label": glob_def.get("label", rel),
                    "phase": glob_def.get("phase", "delivery"),
                    "kind": glob_def.get("kind", "artifact"),
                    "required_for_complete": glob_def.get("required_for_complete", False),
                }
            )
    return items


def detect_data_mode(root: Path, backlog: Path, specs_dir: Path) -> str:
    template = ROOT
    showcase = template / "docs/examples/hub-showcase/mvp-backlog.md"
    showcase_specs = template / "docs/examples/hub-showcase/specs"
    has_real_req = backlog.exists() and bool(BACKLOG_REQ_ROW_RE.search(backlog.read_text(encoding="utf-8")))
    uses_showcase_backlog = showcase.exists() and backlog.resolve() == showcase.resolve()
    uses_showcase_specs = showcase_specs.exists() and specs_dir.resolve() == showcase_specs.resolve()
    if uses_showcase_backlog and uses_showcase_specs:
        return "showcase"
    if has_real_req and uses_showcase_specs:
        return "mixed"
    if root != template:
        return "real"
    if uses_showcase_backlog and not has_real_req:
        return "showcase"
    if has_real_req:
        return "real"
    return "showcase"


def parse_cards(cards_dir: Path, root: Path | None = None) -> list[dict]:
    out = []
    if not cards_dir.exists():
        return out
    root = root or cards_dir.parent.parent.parent
    for p in sorted(cards_dir.glob("CARD-*.md")):
        meta = load_frontmatter(p)
        status = (meta.get("status") or "open").lower()
        out.append(
            {
                "id": (meta.get("id") or p.stem).upper(),
                "status": status,
                "phase": meta.get("phase"),
                "title": meta.get("title") or p.stem,
                "path": str(p.relative_to(root)) if p.is_relative_to(root) else str(p),
                "opened_at": meta.get("opened_at"),
                "done_at": meta.get("done_at"),
                "req_ids": meta.get("req_ids") or [],
            }
        )
    return out


def parse_mvp_phases(root: Path) -> list[dict]:
    for rel in ("docs/planning/mvp-phases.md", "planning/mvp-phases.md"):
        path = root / rel
        if path.exists():
            break
    else:
        return []
    phases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line or "Fase" in line:
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if not parts or not parts[0].startswith("FASE-"):
            continue
        phases.append(
            {
                "id": parts[0],
                "label": parts[1] if len(parts) > 1 else parts[0],
                "order": int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None,
            }
        )
    return phases


def parse_retro_index(root: Path) -> dict[str, str]:
    path = root / "docs/meta/retrospectives/index.md"
    if not path.exists():
        path = ROOT / "docs/meta/retrospectives/index.md"
    status_by_phase: dict[str, str] = {}
    if not path.exists():
        return status_by_phase
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line or "Fase" in line:
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if parts and parts[0].startswith("FASE-"):
            status_by_phase[parts[0]] = parts[1].lower() if len(parts) > 1 else "pending"
    return status_by_phase


def phases_completed(milestones: list) -> set[str]:
    done = set()
    for m in milestones:
        if m.get("activity") == "phase_delivery_end" and m.get("ended_at") and m.get("phase"):
            done.add(m["phase"])
    return done


def phase_card_stats(cards: list[dict], phase_id: str) -> dict:
    phase_cards = [c for c in cards if c.get("phase") == phase_id]
    total = len(phase_cards)
    done = sum(1 for c in phase_cards if c["status"] == "done")
    in_prog = sum(1 for c in phase_cards if c["status"] == "in_progress")
    open_c = sum(1 for c in phase_cards if c["status"] in ("open", "ready", "todo", "pending"))
    pct = int(round(100 * done / total)) if total else 0
    return {"total": total, "done": done, "in_progress": in_prog, "open": open_c, "progress_pct": pct}


def derive_product_phase_status(cards: list[dict], phase_id: str, completed_milestones: set[str]) -> str:
    stats = phase_card_stats(cards, phase_id)
    if phase_id in completed_milestones or (stats["total"] and stats["done"] == stats["total"]):
        return "complete"
    if stats["in_progress"] or stats["done"] > 0:
        return "in_progress"
    return "pending"


def bootstrap_progress(cfg: dict) -> tuple[int | None, int | None, str | None]:
    bootstrap = cfg.get("bootstrap") or {}
    sections = bootstrap.get("sections") or {}
    if not sections:
        if bootstrap.get("status") == "complete":
            return None, None, None
        return 0, 0, None
    done = sum(1 for v in sections.values() if v in ("complete", "done", "skipped"))
    total = len(sections)
    pending = next((k.replace("_", " ").upper() for k, v in sections.items() if v not in ("complete", "done", "skipped")), None)
    return done, total, pending


def phase_milestone_dates(milestones: list, phase_id: str) -> dict[str, str | None]:
    activity_for_lifecycle = {
        "discovery": {"discovery"},
        "bootstrap": {"bootstrap"},
        "design": {"design_mock", "design_approved"},
        "mvp_planning": {"mvp_planning_end"},
    }
    started: str | None = None
    ended: str | None = None
    for m in milestones:
        act = m.get("activity") or ""
        ph = m.get("phase") or ""
        if phase_id.startswith("FASE-"):
            if ph != phase_id:
                continue
        elif phase_id in activity_for_lifecycle:
            if act not in activity_for_lifecycle[phase_id]:
                continue
        else:
            continue
        if m.get("started_at"):
            if not started or str(m["started_at"]) < started:
                started = m["started_at"]
        if m.get("ended_at"):
            if not ended or str(m["ended_at"]) > ended:
                ended = m["ended_at"]
    return {"started_at": started, "ended_at": ended}


def card_effort_from_timeline(timeline: dict, card_id: str) -> dict | None:
    human = 0
    ai = 0
    for r in timeline.get("rounds") or []:
        if (r.get("card_id") or "").upper() == card_id.upper():
            human += int(r.get("human_active_seconds") or 0)
            ai += int(r.get("ai_execution_seconds") or 0)
    if human or ai:
        return {"human_active_seconds": human, "ai_execution_seconds": ai}
    return None


def parse_vision_review(root: Path) -> dict:
    for rel in ("docs/discovery/vision-review.md", "discovery/vision-review.md"):
        path = root / rel
        if path.exists():
            break
    else:
        return {"checklist_ok": None, "items": []}
    text = path.read_text(encoding="utf-8")
    items: list[dict] = []
    checklist_ok = None
    for line in text.splitlines():
        m = re.match(r"^-\s+\[([ xX])\]\s+(.+)$", line.strip())
        if m:
            items.append({"label": m.group(2).strip(), "ok": m.group(1).lower() == "x"})
    status_m = re.search(r"\|\s*Status\s*\|\s*([^|]+)\|", text, re.I)
    if status_m:
        st = status_m.group(1).strip().lower()
        checklist_ok = st == "ok"
    elif items:
        checklist_ok = all(i["ok"] for i in items)
    return {"checklist_ok": checklist_ok, "items": items}


def parse_traceability_matrix(root: Path) -> dict[str, dict]:
    for rel in ("docs/traceability-matrix.md", "traceability-matrix.md"):
        path = root / rel
        if path.exists():
            break
    else:
        return {}
    rows: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line or "REQ_ID" in line:
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if parts and parts[0].upper().startswith("REQ-"):
            rid = parts[0].upper()
            rows[rid] = {
                "matrix_status": parts[12] if len(parts) > 12 else None,
                "test_unit": parts[5] if len(parts) > 5 else None,
                "test_integ": parts[6] if len(parts) > 6 else None,
            }
    return rows


def build_empty_hints(root: Path, timeline: dict, data_dir: Path) -> dict[str, str]:
    hints: dict[str, str] = {}
    if not (timeline.get("rounds") or timeline.get("milestones")):
        hints["process"] = "Registre rodadas em docs/meta/process-timeline.yaml e rode make hub-build."
    last_run = data_dir / "quality.data.json"
    q = load_json(last_run)
    if not q.get("last_run"):
        hints["quality"] = "Exporte uma execução de testes (export-quality-run.sh) para alimentar Qualidade."
    if not hints:
        return {}
    return hints


def build_lifecycle_phases(
    cfg: dict,
    cards: list[dict],
    milestones: list,
    mvp_phases: list[dict],
    retro_index: dict[str, str],
) -> list[dict]:
    project = cfg.get("project") or {}
    has_frontend = project.get("has_frontend") is True or (
        project.get("has_frontend") is None and bool(cfg.get("design"))
    )
    discovery = cfg.get("discovery") or {}
    bootstrap = cfg.get("bootstrap") or {}
    mvp_planning = cfg.get("mvp_planning") or {}
    design = cfg.get("design") or {}
    completed_ms = phases_completed(milestones)

    phases: list[dict] = []

    disc_status = discovery.get("status", "pending")
    if discovery.get("skipped"):
        disc_status = "skipped"
    phases.append(
        {
            "id": "discovery",
            "label": "Fase 0 — Descoberta",
            "type": "lifecycle",
            "status": "complete" if disc_status == "complete" else ("skipped" if disc_status == "skipped" else "pending"),
            "progress_pct": 100 if disc_status in ("complete", "skipped") else 0,
            "blockers": [] if disc_status in ("complete", "skipped") else ["discovery.status pendente"],
        }
    )

    boot_done, boot_total, boot_pending = bootstrap_progress(cfg)
    if boot_total is None and bootstrap.get("status") == "complete":
        boot_pct = 100
        boot_sections_done = None
        boot_sections_total = None
    elif boot_total:
        boot_pct = int(round(100 * boot_done / boot_total))
        boot_sections_done = boot_done
        boot_sections_total = boot_total
    else:
        boot_pct = 0
        boot_sections_done = 0
        boot_sections_total = 0
    boot_status = "complete" if bootstrap.get("status") == "complete" else ("in_progress" if boot_done else "pending")
    boot_phase = {
        "id": "bootstrap",
        "label": "Fase 1 — Bootstrap",
        "type": "lifecycle",
        "status": boot_status,
        "progress_pct": boot_pct,
        "blockers": [f"Bloco {boot_pending} pendente"] if boot_pending else [],
    }
    if boot_sections_total is not None:
        boot_phase["sections_done"] = boot_sections_done
        boot_phase["sections_total"] = boot_sections_total
    phases.append(boot_phase)

    if has_frontend:
        des_st = design.get("status", "draft")
        phases.append(
            {
                "id": "design",
                "label": "Design — Aprovação visual",
                "type": "lifecycle",
                "status": "complete" if des_st == "approved" else ("in_progress" if des_st == "in_review" else "pending"),
                "progress_pct": 100 if des_st == "approved" else (60 if des_st == "in_review" else 20),
                "blockers": [] if des_st == "approved" else [f"design.status: {des_st}"],
            }
        )

    mvp_st = mvp_planning.get("status", "pending")
    phases.append(
        {
            "id": "mvp_planning",
            "label": "Fase 2 — Planejamento MVP",
            "type": "lifecycle",
            "status": "complete" if mvp_st == "complete" else ("in_progress" if mvp_st == "in_progress" else "pending"),
            "progress_pct": 100 if mvp_st == "complete" else (40 if cards else 0),
            "blockers": [] if mvp_st == "complete" else ["mvp_planning.status pendente"],
            "cards_planned": len(cards),
        }
    )

    for mp in mvp_phases:
        pid = mp["id"]
        stats = phase_card_stats(cards, pid)
        st = derive_product_phase_status(cards, pid, completed_ms)
        blockers = []
        if stats["open"]:
            blockers.append(f"{stats['open']} card(s) open")
        if stats["in_progress"]:
            blockers.append(f"{stats['in_progress']} em andamento")
        retro = retro_index.get(pid, "pending")
        if st == "complete" and retro == "pending":
            blockers.append("retro pendente")
        phases.append(
            {
                "id": pid,
                "label": f"{pid} — {mp.get('label', '')}".strip(" —"),
                "type": "delivery_phase",
                "status": st,
                "progress_pct": stats["progress_pct"],
                "blockers": blockers,
                "cards": stats,
                "retro_status": retro,
            }
        )

    for p in phases:
        dates = phase_milestone_dates(milestones, p["id"])
        if dates.get("started_at"):
            p["started_at"] = dates["started_at"]
        if dates.get("ended_at"):
            p["ended_at"] = dates["ended_at"]

    return phases


def parse_spec_status(specs_dir: Path, req_id: str) -> str | None:
    if not specs_dir.exists():
        return None
    for p in specs_dir.glob(f"{req_id}*.md"):
        return load_frontmatter(p).get("status")
    return None


def enrich_deliveries(
    root: Path,
    delivery_entries: list[dict],
    cards: list[dict],
    cards_dir: Path,
    specs_dir: Path,
    quality: dict,
    timeline: dict | None = None,
    matrix_rows: dict[str, dict] | None = None,
) -> list[dict]:
    card_by_id = {c["id"]: c for c in cards}
    req_quality = {r["req_id"]: r for r in quality.get("requirements") or [] if r.get("req_id")}
    log_by_card = {e["card_id"]: e for e in delivery_entries}
    all_card_ids = sorted(set(list(card_by_id.keys()) + list(log_by_card.keys())))
    matrix_rows = matrix_rows or {}
    timeline = timeline or {}

    enriched = []
    for cid in all_card_ids:
        card = card_by_id.get(cid, {})
        log = log_by_card.get(cid, {})
        card_path = cards_dir / f"{cid}.md"
        if card_path.exists():
            meta = load_frontmatter(card_path)
            req_ids = meta.get("req_ids") or log.get("req_ids") or []
            phase = meta.get("phase") or log.get("phase")
            opened_at = meta.get("opened_at") or log.get("started_at")
            done_at = meta.get("done_at") or log.get("ended_at")
            card_status = meta.get("status") or card.get("status")
            rel_path = str(card_path.relative_to(root)) if card_path.is_relative_to(root) else str(card_path)
        else:
            req_ids = log.get("req_ids") or []
            phase = log.get("phase")
            opened_at = log.get("started_at")
            done_at = log.get("ended_at")
            card_status = "done" if "conclu" in log.get("status", "").lower() else "unknown"
            rel_path = log.get("card_path")

        req_details = []
        gap_total = 0
        for rid in req_ids:
            rid_up = rid.upper() if isinstance(rid, str) else rid
            rq = req_quality.get(rid_up, {})
            gaps = rq.get("gap_layers") or []
            gap_total += len(gaps)
            mx = matrix_rows.get(rid_up, {})
            req_details.append(
                {
                    "req_id": rid_up,
                    "spec_status": parse_spec_status(specs_dir, rid_up),
                    "quality_gaps": len(gaps),
                    "matrix_status": mx.get("matrix_status"),
                    "test_unit": mx.get("test_unit"),
                    "test_integ": mx.get("test_integ"),
                }
            )

        effort = card_effort_from_timeline(timeline, cid)
        row = {
            "card_id": cid,
            "title": log.get("title") or card.get("title") or cid,
            "phase": phase,
            "status": log.get("status") or card_status,
            "card_status": card_status,
            "req_ids": [r.upper() if isinstance(r, str) else r for r in req_ids],
            "req_details": req_details,
            "quality_gap_count": gap_total,
            "tdd_red_green": log.get("tdd_red_green"),
            "started_at": opened_at,
            "ended_at": done_at,
            "branch": log.get("branch"),
            "pr": log.get("pr"),
            "card_path": rel_path or log.get("card_path"),
        }
        if effort:
            row["effort"] = effort
        enriched.append(row)

    enriched.sort(key=lambda x: (x.get("ended_at") or x.get("started_at") or x["card_id"]), reverse=True)
    return enriched


def git_last_commit(root: Path, rel_path: str) -> dict | None:
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%aI|%s|%an", "--", rel_path],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if not out:
            return None
        parts = out.split("|", 2)
        return {"at": parts[0], "message": parts[1] if len(parts) > 1 else "", "author": parts[2] if len(parts) > 2 else ""}
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def has_tracked_process_activity(
    timeline: dict,
    delivery_entries: list[dict],
    cards: list[dict],
) -> bool:
    """True quando há entregas, cards ativos ou métricas — habilita feed de artefatos."""
    if timeline.get("rounds") or timeline.get("sessions"):
        return True
    for m in timeline.get("milestones") or []:
        if m.get("started_at") or m.get("ended_at"):
            return True
    if delivery_entries:
        return True
    for c in cards:
        if c.get("done_at") or c.get("opened_at"):
            return True
        if (c.get("status") or "").lower() in ("done", "in_progress", "closed"):
            return True
    return False


def build_activity(
    root: Path,
    manifest_items: list[dict],
    timeline: dict,
    delivery_entries: list[dict],
    cards: list[dict],
    limit: int = 40,
) -> list[dict]:
    events: list[dict] = []
    include_artifacts = has_tracked_process_activity(timeline, delivery_entries, cards)

    seen_paths: set[str] = set()
    for art in manifest_items:
        if not include_artifacts:
            continue
        rel = art.get("path")
        full: Path = art.get("resolved")
        if not rel or not full or not full.exists() or rel in seen_paths:
            continue
        seen_paths.add(rel)
        mtime = datetime.fromtimestamp(full.stat().st_mtime, tz=timezone.utc).isoformat()
        git_info = git_last_commit(root, rel)
        at = git_info["at"] if git_info else mtime
        summary = f"{art.get('label', rel)} atualizado"
        events.append(
            {
                "at": at,
                "source": "artifact",
                "phase": art.get("phase"),
                "kind": art.get("kind"),
                "path": rel,
                "summary": summary,
                "git_message": git_info.get("message") if git_info else None,
            }
        )

    for r in timeline.get("rounds") or []:
        if r.get("source") not in ("agent_turn", "milestone", "manual"):
            continue
        events.append(
            {
                "at": r.get("at"),
                "source": r.get("source"),
                "phase": r.get("phase"),
                "kind": "timeline_round",
                "path": "docs/meta/process-timeline.yaml",
                "summary": f"Rodada {r.get('activity', '—')}" + (f" ({r.get('card_id')})" if r.get("card_id") else ""),
                "card_id": r.get("card_id"),
            }
        )

    for e in delivery_entries:
        if e.get("ended_at") or e.get("started_at"):
            events.append(
                {
                    "at": e.get("ended_at") or e.get("started_at"),
                    "source": "delivery_log",
                    "phase": e.get("phase") or "delivery",
                    "kind": "delivery",
                    "path": "docs/delivery-log.md",
                    "summary": f"Entrega {e['card_id']}: {e.get('status', '—')}",
                    "card_id": e["card_id"],
                }
            )

    for c in cards:
        if c.get("done_at"):
            events.append(
                {
                    "at": c["done_at"],
                    "source": "card",
                    "phase": c.get("phase") or "delivery",
                    "kind": "card",
                    "path": c.get("path"),
                    "summary": f"{c['id']} concluído",
                    "card_id": c["id"],
                }
            )
        elif c.get("opened_at"):
            events.append(
                {
                    "at": c["opened_at"],
                    "source": "card",
                    "phase": c.get("phase") or "delivery",
                    "kind": "card",
                    "path": c.get("path"),
                    "summary": f"{c['id']} aberto",
                    "card_id": c["id"],
                }
            )

    def sort_key(ev: dict) -> str:
        return ev.get("at") or ""

    events.sort(key=sort_key, reverse=True)
    return events[:limit]


def build_payload(
    root: Path,
    config_path: Path,
    cards_dir: Path,
    specs_dir: Path,
    backlog: Path,
    data_dir: Path,
) -> dict:
    cfg = load_yaml(config_path)
    manifest = load_artifact_manifest(root)
    manifest_items = expand_manifest_paths(root, manifest)

    timeline_path = root / "docs/meta/process-timeline.yaml"
    if not timeline_path.exists():
        timeline_path = ROOT / "docs/meta/process-timeline.yaml"
    timeline = load_yaml(timeline_path)
    milestones = timeline.get("milestones") or []

    cards = parse_cards(cards_dir, root)
    mvp_phases = parse_mvp_phases(root)
    retro_index = parse_retro_index(root)

    lifecycle_phases = build_lifecycle_phases(cfg, cards, milestones, mvp_phases, retro_index)

    delivery_path = resolve_delivery_log(root)
    delivery_entries = parse_delivery_log(delivery_path)
    quality = load_json(data_dir / "quality.data.json")
    matrix_rows = parse_traceability_matrix(root)
    deliveries = enrich_deliveries(
        root, delivery_entries, cards, cards_dir, specs_dir, quality, timeline, matrix_rows
    )

    activity = build_activity(root, manifest_items, timeline, delivery_entries, cards)
    discovery = parse_vision_review(root)
    empty_hints = build_empty_hints(root, timeline, data_dir)

    data_mode = detect_data_mode(root, backlog, specs_dir)

    complete_count = sum(1 for p in lifecycle_phases if p.get("status") == "complete")
    in_progress = next((p["id"] for p in lifecycle_phases if p.get("status") == "in_progress"), None)
    if not in_progress:
        in_progress = next((p["id"] for p in lifecycle_phases if p.get("status") == "pending"), None)

    return {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "data_mode": data_mode,
        "discovery": discovery,
        "lifecycle": {
            "phases": lifecycle_phases,
            "phases_complete": complete_count,
            "phases_total": len(lifecycle_phases),
            "current_phase_id": in_progress,
        },
        "deliveries": deliveries,
        "activity": activity,
        "report": {
            "delivery_count": len(deliveries),
            "activity_count": len(activity),
            "showcase_banner": data_mode in ("showcase", "mixed"),
            "empty_hints": empty_hints,
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--config", type=Path)
    p.add_argument("--cards-dir", type=Path)
    p.add_argument("--specs-dir", type=Path)
    p.add_argument("--backlog", type=Path)
    p.add_argument("--data-dir", type=Path, required=True)
    p.add_argument("--json", type=Path, required=True)
    args = p.parse_args()
    root = args.root.resolve()
    config = args.config or root / "project.config.yaml"
    cards_dir = args.cards_dir or root / "docs/tracking/cards"
    if not cards_dir.exists():
        cards_dir = root / "tracking/cards"
    specs_dir = args.specs_dir or root / "docs/specs"
    if not specs_dir.is_dir():
        specs_dir = root / "specs"
    backlog = args.backlog or root / "docs/backlog/mvp-backlog.md"
    if not backlog.exists():
        backlog = root / "backlog/mvp-backlog.md"

    payload = build_payload(root, config, cards_dir, specs_dir, backlog, args.data_dir)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
