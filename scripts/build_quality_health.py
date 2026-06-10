#!/usr/bin/env python3
"""Aggregate backlog, specs, matrix and last test run → quality-health JSON."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from quality_spec_parser import (  # noqa: E402
    LAYER_LABELS,
    PANEL_LAYERS,
    load_yaml,
    normalize_layer,
    merge_required_layers,
    parse_backlog,
    parse_spec,
    set_paths as set_parser_paths,
)

_CTX: dict[str, Path] = {
    "root": ROOT,
    "config": ROOT / "project.config.yaml",
    "backlog": ROOT / "docs/backlog/mvp-backlog.md",
    "matrix": ROOT / "docs/traceability-matrix.md",
    "specs_dir": ROOT / "docs/specs",
    "json_out": ROOT / "docs/meta/quality-health/quality-health.data.json",
    "manifest": ROOT / "docs/meta/quality-manifest.yaml",
    "last_run_json": ROOT / "docs/meta/quality-runs/latest.json",
    "last_run_manual": ROOT / "docs/meta/quality-runs/manual.yaml",
}


def load_config() -> dict:
    return load_yaml(_CTX["config"])



def parse_matrix() -> dict[str, dict]:
    path = _CTX["matrix"]
    out: dict[str, dict] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "REQ-" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 12:
            continue
        req_id = parts[1]
        if not req_id.startswith("REQ-"):
            continue
        out[req_id] = {
            "spec": parts[4],
            "unit": parts[6],
            "integration": parts[7],
            "openapi": parts[8],
            "e2e": parts[9],
            "status": parts[12] if len(parts) > 12 else "backlog",
        }
    return out


def load_last_run(cfg: dict) -> tuple[dict, str]:
    qh = cfg.get("quality_health") or {}
    json_path = _CTX.get("last_run_json") or _CTX["root"] / (
        qh.get("last_run_json") or "docs/meta/quality-runs/latest.json"
    )
    manual_path = _CTX.get("last_run_manual") or _CTX["root"] / (
        qh.get("last_run_manual") or "docs/meta/quality-runs/manual.yaml"
    )
    if not json_path.is_absolute():
        json_path = _CTX["root"] / json_path
    if not manual_path.is_absolute():
        manual_path = _CTX["root"] / manual_path
    if json_path.exists():
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return normalize_last_run(data), "ci_json"
        except json.JSONDecodeError:
            pass
    manual = load_yaml(manual_path)
    if manual.get("tests") or manual.get("layers") or manual.get("overall") not in (None, "unknown"):
        return normalize_last_run(manual), "manual_yaml"
    return {}, "none"


def normalize_last_run(data: dict) -> dict:
    """Normaliza camada contract → integration em testes e resumo por camada."""
    if not data:
        return data
    out = dict(data)
    out["tests"] = normalize_tests_run(out.get("tests") or [])
    layers = dict(out.get("layers") or {})
    contract = layers.pop("contract", None)
    if contract:
        integration = dict(layers.get("integration") or {})
        for key in ("passed", "failed", "skipped"):
            integration[key] = (integration.get(key) or 0) + (contract.get(key) or 0)
        statuses = [integration.get("status"), contract.get("status")]
        if "fail" in statuses:
            integration["status"] = "fail"
        elif "partial" in statuses:
            integration["status"] = "partial"
        elif integration.get("status") in (None, "unknown") and contract.get("status"):
            integration["status"] = contract.get("status")
        layers["integration"] = integration
    out["layers"] = layers
    return out


def file_exists(root: Path, rel: str | None) -> bool:
    if not rel:
        return False
    p = root / rel
    return p.is_file()


def normalize_tests_run(tests: list) -> list[dict]:
    out = []
    for t in tests:
        if not isinstance(t, dict):
            continue
        item = dict(t)
        item["layer"] = normalize_layer(item.get("layer"))
        out.append(item)
    return out


def match_run_status(tests: list, layer: str, scenario: str, file_path: str | None) -> str | None:
    layer = normalize_layer(layer)
    match_layers = {layer}
    if layer == "integration":
        match_layers.add("contract")
    for t in tests:
        if not isinstance(t, dict):
            continue
        tl = normalize_layer(t.get("layer"))
        if tl not in match_layers and t.get("layer") not in match_layers:
            continue
        if file_path and t.get("file") and t.get("file") == file_path:
            return t.get("status")
        if t.get("scenario") and scenario and t.get("scenario") == scenario:
            return t.get("status")
    return None


def resolve_layer_status(
    layer: str,
    required: bool,
    cases: list[dict],
    tests_run: list,
    root: Path,
) -> dict:
    if not required:
        return {"required": False, "built": False, "status": "not_required", "cases": []}

    case_rows = []
    any_built = False
    worst = "not_required"
    priority = {
        "fail": 5,
        "missing": 4,
        "pending": 3,
        "unknown": 2,
        "pass": 1,
        "skip": 1,
        "not_required": 0,
    }

    if not cases:
        case_rows.append({"scenario": "(plano não preenchido)", "file": None, "status": "missing"})
        return {
            "required": True,
            "built": False,
            "status": "missing",
            "cases": case_rows,
        }

    for c in cases:
        fp = c.get("file")
        built = file_exists(root, fp) if fp else False
        if built:
            any_built = True
        run_st = match_run_status(tests_run, layer, c.get("scenario", ""), fp)
        if run_st:
            st = run_st
        elif c.get("spec_status") in ("pending", "n/a"):
            st = "pending" if not built else "unknown"
        elif not built:
            st = "missing"
        else:
            st = "unknown"
        case_rows.append(
            {
                "scenario": c.get("scenario"),
                "business_flow": c.get("business_flow"),
                "persona": c.get("persona"),
                "steps_summary": c.get("steps_summary"),
                "expected_result": c.get("expected_result"),
                "file": fp,
                "status": st,
            }
        )
        if priority.get(st, 0) > priority.get(worst, 0):
            worst = st

    if worst == "not_required":
        worst = "missing" if not any_built else "unknown"

    return {"required": True, "built": any_built, "status": worst, "cases": case_rows}


def load_coverage(cfg: dict, last_run: dict) -> dict:
    cov_cfg = cfg.get("coverage") or {}
    qh = cfg.get("quality_health") or {}
    out = {}
    run_cov = last_run.get("coverage") or {}
    for side in ("backend", "frontend"):
        threshold = (cov_cfg.get(side) or {}).get("threshold")
        rc = run_cov.get(side) or {}
        lines = rc.get("lines")
        meets = rc.get("meets_threshold")
        if meets is None and lines is not None and threshold is not None:
            meets = float(lines) >= float(threshold)
        out[side] = {
            "lines": lines,
            "branches": rc.get("branches"),
            "threshold": threshold or rc.get("threshold"),
            "meets_threshold": meets,
            "artifact": (qh.get("coverage_artifacts") or {}).get(side),
        }
    return out


BUSINESS_STATUS = {
    "pass": "Aprovado",
    "fail": "Falhou",
    "missing": "Teste não criado",
    "pending": "Planejado",
    "unknown": "Não executado",
    "skip": "Ignorado",
    "not_required": "Não aplicável",
}

HEALTH_LABELS = (
    (90, "Excelente"),
    (75, "Bom"),
    (50, "Atenção"),
    (0, "Crítico"),
)


def health_label(score: float) -> str:
    for threshold, label in HEALTH_LABELS:
        if score >= threshold:
            return label
    return "Crítico"


def compute_analytics(requirements: list[dict], coverage: dict, gaps: list[dict]) -> dict:
    cases: list[dict] = []
    for req in requirements:
        for layer, linfo in (req.get("layers") or {}).items():
            if not linfo.get("required"):
                continue
            for c in linfo.get("cases") or []:
                cases.append({**c, "layer": layer, "req_id": req.get("req_id")})

    weights = {
        "pass": 100,
        "skip": 95,
        "unknown": 55,
        "pending": 35,
        "missing": 5,
        "fail": 0,
    }
    scorable = [c for c in cases if c.get("status") not in ("not_required", None)]
    health_score = (
        round(sum(weights.get(c.get("status", "unknown"), 0) for c in scorable) / len(scorable))
        if scorable
        else 0
    )

    by_status: dict[str, int] = {}
    for st in weights:
        by_status[st] = sum(1 for c in scorable if c.get("status") == st)

    by_layer: dict[str, dict] = {}
    for layer in PANEL_LAYERS:
        layer_cases = [c for c in scorable if c.get("layer") == layer]
        if not layer_cases:
            continue
        passed = sum(1 for c in layer_cases if c.get("status") == "pass")
        by_layer[layer] = {
            "label": LAYER_LABELS[layer],
            "total": len(layer_cases),
            "pass": passed,
            "fail": sum(1 for c in layer_cases if c.get("status") == "fail"),
            "pending": sum(1 for c in layer_cases if c.get("status") in ("pending", "missing")),
            "pct_pass": round(100 * passed / len(layer_cases), 1),
        }

    cov_lines = []
    for side in ("backend", "frontend"):
        c = coverage.get(side) or {}
        if c.get("lines") is not None:
            cov_lines.append(float(c["lines"]))
    avg_coverage = round(sum(cov_lines) / len(cov_lines), 1) if cov_lines else None

    return {
        "health_score": health_score,
        "health_label": health_label(health_score),
        "tests_total": len(scorable),
        "tests_pass": by_status.get("pass", 0),
        "tests_fail": by_status.get("fail", 0),
        "tests_pending": by_status.get("pending", 0) + by_status.get("missing", 0),
        "tests_unknown": by_status.get("unknown", 0),
        "by_status": by_status,
        "by_layer": by_layer,
        "avg_coverage_pct": avg_coverage,
        "gaps_count": len(gaps),
    }


def build_report(reqs: list[dict], gaps: list[dict], last_run: dict, run_source: str) -> dict:
    total = len(reqs)
    fully_green = sum(
        1
        for r in reqs
        if r.get("all_layers_green")
    )
    gap_count = len(gaps)
    func_gaps = sum(1 for g in gaps if g.get("req_kind") == "functional")
    nfr_gaps = sum(1 for g in gaps if g.get("req_kind") == "non_functional")
    return {
        "title": "Saúde da qualidade",
        "subtitle": "TDD, cobertura e rastreio REQ → testes",
        "last_run_at": last_run.get("run_at"),
        "last_run_source": run_source,
        "last_run_overall": last_run.get("overall", "unknown"),
        "req_total": total,
        "req_fully_green_pct": round(100 * fully_green / total, 1) if total else 0,
        "req_fully_green": fully_green,
        "gap_count": gap_count,
        "gap_functional": func_gaps,
        "gap_non_functional": nfr_gaps,
    }


def build_quality_data() -> dict:
    cfg = load_config()
    root = _CTX["root"]
    last_run, run_source = load_last_run(cfg)
    tests_run = normalize_tests_run(last_run.get("tests") or [])
    e2e_enabled = bool((cfg.get("e2e") or {}).get("enabled"))

    backlog_reqs = parse_backlog()
    matrix = parse_matrix()
    requirements = []
    gaps = []
    by_layer: dict[str, list] = {layer: [] for layer in PANEL_LAYERS}

    for br in backlog_reqs:
        req_id = br["req_id"]
        spec = parse_spec(req_id)
        req_kind = spec.get("req_kind") or br.get("req_kind", "functional")
        required = merge_required_layers(spec.get("required_layers") or {l: False for l in PANEL_LAYERS})
        if br.get("critical_flow") and e2e_enabled:
            required["e2e"] = True

        layers_out = {}
        for layer in PANEL_LAYERS:
            if layer == "e2e" and not e2e_enabled:
                required[layer] = required.get(layer) and br.get("critical_flow")
            cases = (spec.get("cases") or {}).get(layer, [])
            layers_out[layer] = resolve_layer_status(
                layer, required.get(layer, False), cases, tests_run, root
            )
            for case in layers_out[layer].get("cases") or []:
                by_layer[layer].append(
                    {
                        "req_id": req_id,
                        "req_kind": req_kind,
                        "title": br.get("title"),
                        "scenario": case.get("scenario"),
                        "business_flow": case.get("business_flow"),
                        "persona": case.get("persona"),
                        "steps_summary": case.get("steps_summary"),
                        "expected_result": case.get("expected_result"),
                        "file": case.get("file"),
                        "status": case.get("status"),
                    }
                )

        bad_layers = [
            LAYER_LABELS[l]
            for l in PANEL_LAYERS
            if layers_out[l].get("required")
            and layers_out[l].get("status") not in ("pass", "skip", "unknown")
        ]
        all_green = (
            spec.get("exists")
            and not bad_layers
            and all(
                layers_out[l].get("status") in ("pass", "skip", "not_required", "unknown")
                for l in PANEL_LAYERS
                if layers_out[l].get("required")
            )
        )

        item = {
            **br,
            "req_kind": req_kind,
            "spec_path": spec.get("path"),
            "spec_status": spec.get("status"),
            "matrix_status": (matrix.get(req_id) or {}).get("status"),
            "layers": layers_out,
            "all_layers_green": all_green,
            "gap_layers": bad_layers,
        }
        requirements.append(item)

        if bad_layers or not spec.get("exists"):
            gaps.append(
                {
                    "req_id": req_id,
                    "req_kind": req_kind,
                    "priority": br.get("priority"),
                    "title": br.get("title"),
                    "spec_missing": not spec.get("exists"),
                    "gap_layers": bad_layers or (["spec ausente"] if not spec.get("exists") else []),
                }
            )

    gaps.sort(
        key=lambda g: (
            0 if g.get("priority") == "P0" else 1 if g.get("priority") == "P1" else 2,
            g.get("req_id") or "",
        )
    )

    coverage = load_coverage(cfg, last_run)
    analytics = compute_analytics(requirements, coverage, gaps)

    return {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "config": {
            "e2e_enabled": e2e_enabled,
            "quality_health_enabled": bool((cfg.get("quality_health") or {}).get("enabled", True)),
        },
        "last_run": {
            "source": run_source,
            "run_at": last_run.get("run_at"),
            "commit": last_run.get("commit"),
            "ci_job": last_run.get("ci_job"),
            "overall": last_run.get("overall", "unknown"),
            "layers_summary": last_run.get("layers") or {},
        },
        "coverage": coverage,
        "requirements": requirements,
        "by_layer": by_layer,
        "gaps": gaps,
        "analytics": analytics,
        "layer_labels": {k: LAYER_LABELS[k] for k in PANEL_LAYERS},
        "status_legend": {
            "not_required": "Não exigido na spec",
            "missing": "Obrigatório — teste não construído",
            "pending": "Plano TDD pendente",
            "unknown": "Teste existe — sem última execução",
            "pass": "Última execução passou",
            "fail": "Última execução falhou",
            "skip": "Ignorado na última execução",
        },
        "business_status": BUSINESS_STATUS,
        "report": build_report(requirements, gaps, last_run, run_source),
    }


def set_paths(**kwargs: Path | None) -> None:
    for key, val in kwargs.items():
        if val is not None:
            _CTX[key] = val
    set_parser_paths(
        root=kwargs.get("root"),
        config=kwargs.get("config"),
        backlog=kwargs.get("backlog"),
        matrix=kwargs.get("matrix"),
        specs_dir=kwargs.get("specs_dir"),
        manifest=kwargs.get("manifest"),
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path)
    p.add_argument("--config", type=Path)
    p.add_argument("--backlog", type=Path)
    p.add_argument("--matrix", type=Path)
    p.add_argument("--specs-dir", type=Path)
    p.add_argument("--json", type=Path)
    p.add_argument("--last-run-json", type=Path)
    p.add_argument("--last-run-manual", type=Path)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.root:
        _CTX["root"] = args.root
        set_parser_paths(root=args.root)
    set_paths(
        config=args.config,
        backlog=args.backlog,
        matrix=args.matrix,
        specs_dir=args.specs_dir,
        json_out=args.json,
        last_run_json=args.last_run_json,
        last_run_manual=args.last_run_manual,
    )
    data = build_quality_data()
    out = _CTX["json_out"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"OK: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
