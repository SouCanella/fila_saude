#!/usr/bin/env python3
"""Export CI test results → docs/meta/quality-runs/latest.json."""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from quality_spec_parser import build_req_trace_map, normalize_layer, resolve_req_ids_for_test, set_paths  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "docs/meta/quality-runs/latest.json"


def parse_junit(path: Path, layer: str, trace_map: dict) -> list[dict]:
    layer = normalize_layer(layer)
    tests = []
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        print(f"AVISO: JUnit inválido {path}: {e}", file=sys.stderr)
        return tests
    root = tree.getroot()
    cases = root.findall(".//testcase")
    if not cases and root.tag == "testcase":
        cases = [root]
    for tc in cases:
        name = tc.get("name") or "unnamed"
        classname = tc.get("classname") or ""
        file_hint = tc.get("file") or classname.replace(".", "/")
        failed = tc.find("failure") is not None or tc.find("error") is not None
        skipped = tc.find("skipped") is not None
        if skipped:
            status = "skip"
        elif failed:
            status = "fail"
        else:
            status = "pass"
        msg_el = tc.find("failure") or tc.find("error")
        props = tc.find("properties")
        prop_text = ""
        if props is not None:
            for pr in props.findall("property"):
                prop_text += f" {pr.get('name') or ''}={pr.get('value') or ''}"
        req_ids = resolve_req_ids_for_test(
            layer, file_hint, name, f"{name} {prop_text}", trace_map
        )
        tests.append(
            {
                "id": f"{layer}:{name}",
                "layer": layer,
                "req_ids": req_ids,
                "file": file_hint if file_hint else None,
                "scenario": name,
                "status": status,
                "message": (msg_el.text or "")[:500] if msg_el is not None else None,
            }
        )
    return tests


def parse_coverage_summary(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    if "total" in data:
        t = data["total"]
        lines = t.get("lines") or {}
        branches = t.get("branches") or {}
        return {
            "lines": lines.get("pct"),
            "branches": branches.get("pct"),
        }
    return {}


def layer_stats(tests: list[dict]) -> dict:
    out: dict[str, dict] = {}
    for t in tests:
        layer = normalize_layer(t.get("layer") or "unknown")
        if layer not in out:
            out[layer] = {"passed": 0, "failed": 0, "skipped": 0, "status": "pass"}
        st = t.get("status")
        if st == "pass":
            out[layer]["passed"] += 1
        elif st == "fail":
            out[layer]["failed"] += 1
            out[layer]["status"] = "fail"
        elif st == "skip":
            out[layer]["skipped"] += 1
    for layer, s in out.items():
        if s["failed"] > 0:
            s["status"] = "fail"
        elif s["passed"] == 0 and s["skipped"] > 0:
            s["status"] = "skip"
        else:
            s["status"] = "pass"
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Export quality run JSON from CI artifacts")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--junit-unit-back", type=Path)
    p.add_argument("--junit-unit-front", type=Path)
    p.add_argument("--junit-integration", type=Path)
    p.add_argument("--junit-contract", type=Path)
    p.add_argument("--junit-e2e", type=Path)
    p.add_argument("--coverage-backend", type=Path)
    p.add_argument("--coverage-frontend", type=Path)
    p.add_argument("--commit", default=None)
    p.add_argument("--ci-job", default="ci")
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--backlog", type=Path)
    p.add_argument("--specs-dir", type=Path)
    p.add_argument("--manifest", type=Path)
    args = p.parse_args()

    set_paths(
        root=args.root,
        backlog=args.backlog,
        specs_dir=args.specs_dir,
        manifest=args.manifest,
    )
    trace_map = build_req_trace_map()

    tests: list[dict] = []
    mapping = [
        ("unit_back", args.junit_unit_back),
        ("unit_front", args.junit_unit_front),
        ("integration", args.junit_integration),
        ("contract", args.junit_contract),
        ("e2e", args.junit_e2e),
    ]
    for layer, path in mapping:
        if path and path.exists():
            tests.extend(parse_junit(path, layer, trace_map))

    layers = layer_stats(tests)
    overall = "pass"
    if any(l.get("status") == "fail" for l in layers.values()):
        overall = "fail"
    elif not tests:
        overall = "unknown"

    coverage: dict = {}
    if args.coverage_backend and args.coverage_backend.exists():
        cov = parse_coverage_summary(args.coverage_backend)
        coverage["backend"] = cov
    if args.coverage_frontend and args.coverage_frontend.exists():
        cov = parse_coverage_summary(args.coverage_frontend)
        coverage["frontend"] = cov

    cfg_path = args.root / "project.config.yaml"
    if cfg_path.exists():
        try:
            import yaml  # type: ignore

            cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
            for side in ("backend", "frontend"):
                th = (cfg.get("coverage") or {}).get(side, {}).get("threshold")
                if side in coverage and th is not None and coverage[side].get("lines") is not None:
                    coverage[side]["threshold"] = th
                    coverage[side]["meets_threshold"] = float(coverage[side]["lines"]) >= float(th)
        except Exception:
            pass

    snapshot = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "commit": args.commit,
        "ci_job": args.ci_job,
        "overall": overall,
        "layers": layers,
        "coverage": coverage,
        "tests": tests,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    linked = sum(1 for t in tests if t.get("req_ids"))
    print(f"OK: {args.out} ({len(tests)} teste(s), {linked} com req_ids)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
