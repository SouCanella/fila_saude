#!/usr/bin/env python3
"""Parser compartilhado: specs REQ → plano TDD, mapa de rastreio, validação."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LAYERS = ("unit_back", "unit_front", "integration", "contract", "e2e", "security")
PANEL_LAYERS = ("unit_back", "unit_front", "integration", "e2e", "security")
LAYER_LABELS = {
    "unit_back": "Unitário back",
    "unit_front": "Unitário front",
    "integration": "Integração API (incl. contrato OpenAPI)",
    "contract": "Integração API (incl. contrato OpenAPI)",  # alias legado
    "e2e": "E2E",
    "security": "Segurança",
}
SPEC_LAYER_MAP = {
    "unit_back": [r"unit[aá]rio back", r"unit back", r"dom[ií]nio"],
    "unit_front": [r"unit[aá]rio front", r"unit front", r"componente"],
    "integration": [r"integra[cç][aã]o"],
    "contract": [r"contrato", r"openapi"],
    "e2e": [r"\be2e\b", r"end.to.end"],
    "security": [r"seguran", r"sast", r"threat"],
}
TABLE_SECTIONS = {
    "unit_back": r"### Unitários — back",
    "unit_front": r"### Unitários — front",
    "integration": r"### Integração",
    "e2e": r"### E2E",
}
LAYERS_NEED_FILE = frozenset({"unit_back", "unit_front", "e2e", "integration"})

sys.path.insert(0, str(ROOT / "scripts"))
from modelo_ids import REQ_ID_RE, normalize_req_id  # noqa: E402

REQ_TAG_RE = REQ_ID_RE


def normalize_layer(layer: str | None) -> str:
    if layer == "contract":
        return "integration"
    return layer or "unknown"


def merge_required_layers(required: dict[str, bool]) -> dict[str, bool]:
    """Contrato OpenAPI → mesma camada que integração (sem duplicar no painel)."""
    out = dict(required)
    if out.get("contract"):
        out["integration"] = True
    out["contract"] = False
    return out

_CTX: dict[str, Path] = {
    "root": ROOT,
    "config": ROOT / "project.config.yaml",
    "backlog": ROOT / "docs/backlog/mvp-backlog.md",
    "matrix": ROOT / "docs/traceability-matrix.md",
    "specs_dir": ROOT / "docs/specs",
    "manifest": ROOT / "docs/meta/quality-manifest.yaml",
}


def set_paths(**kwargs: Path | None) -> None:
    for key, val in kwargs.items():
        if val is not None:
            _CTX[key] = val


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        import yaml  # type: ignore
    except ImportError:
        print("ERRO: PyYAML necessário (pip install pyyaml)", file=sys.stderr)
        sys.exit(1)
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


def parse_frontmatter(text: str) -> dict:
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


def find_spec_path(req_id: str) -> Path | None:
    specs_dir = _CTX["specs_dir"]
    if not specs_dir.exists():
        return None
    for p in specs_dir.glob(f"{req_id}*.md"):
        if not p.name.startswith("_"):
            return p
    return None


def parse_backlog() -> list[dict]:
    path = _CTX["backlog"]
    if not path.exists():
        return []
    reqs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "REQ-" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 10:
            continue
        req_id = parts[1]
        if not req_id.startswith("REQ-"):
            continue
        reqs.append(
            {
                "req_id": req_id,
                "phase": parts[2] if parts[2].startswith("FASE-") else None,
                "card_id": parts[3] if parts[3].startswith("CARD-") else None,
                "title": parts[4] or req_id,
                "priority": parts[6] or "—",
                "req_kind": parts[7] if parts[7] in ("functional", "non_functional") else "functional",
                "critical_flow": parts[8].lower() == "true",
            }
        )
    return reqs


def parse_required_layers(spec_text: str) -> dict[str, bool]:
    required = {layer: False for layer in LAYERS}
    block = ""
    in_section = False
    for line in spec_text.splitlines():
        if "## Camadas de teste" in line:
            in_section = True
            continue
        if in_section and line.startswith("## ") and "Camadas" not in line:
            break
        if in_section:
            block += line.lower() + "\n"
    for layer, patterns in SPEC_LAYER_MAP.items():
        for pat in patterns:
            if re.search(rf"-\s*\[x\].*{pat}", block, re.I):
                required[layer] = True
                break
    return merge_required_layers(required)


def _split_table_cells(line: str) -> list[str]:
    return [p.strip() for p in line.split("|")[1:-1]]


def _header_index(header: list[str], *needles: str) -> int | None:
    for i, cell in enumerate(header):
        low = cell.lower()
        if any(n in low for n in needles):
            return i
    return None


def _cell(cells: list[str], idx: int | None, default: str = "") -> str:
    if idx is None or idx >= len(cells):
        return default
    return cells[idx]


def _clean_file(val: str | None) -> str | None:
    if not val or val in ("—", "pending", "n/a", "done", "fail"):
        return None
    if "/" in val or val.endswith((".ts", ".tsx", ".js", ".py", ".spec.ts")):
        return val
    return None


def _status_column_index(header: list[str]) -> int | None:
    for i, cell in enumerate(header):
        low = cell.lower().strip()
        if low == "status" or low.startswith("status "):
            return i
    return None


def _row_from_header(header: list[str], cells: list[str], layer: str) -> dict | None:
    if not cells or not cells[0] or cells[0] in ("—",):
        return None
    h = [c.lower() for c in header]
    status_i = _status_column_index(h)
    spec_status = (_cell(cells, status_i, "pending") or "pending").lower()

    if layer == "e2e":
        biz_i = _header_index(h, "fluxo de negócio", "fluxo")
        persona_i = _header_index(h, "persona")
        steps_i = _header_index(h, "passos")
        expected_i = _header_index(h, "resultado")
        file_i = _header_index(h, "arquivo teste", "arquivo")
        scen_i = _header_index(h, "cenário técnico", "cenário")
        tool_i = _header_index(h, "ferramenta")
        business = _cell(cells, biz_i) or _cell(cells, 0)
        technical = _cell(cells, scen_i)
        if not technical and tool_i is not None:
            technical = _cell(cells, tool_i)
        scenario = technical or business
        if business and technical and business != technical:
            scenario = f"{business} — {technical}"
        return {
            "scenario": scenario,
            "business_flow": business or None,
            "persona": _cell(cells, persona_i) or None,
            "steps_summary": _cell(cells, steps_i) or None,
            "expected_result": _cell(cells, expected_i) or None,
            "file": _clean_file(_cell(cells, file_i)),
            "spec_status": spec_status,
        }

    if layer == "integration":
        endpoint_i = _header_index(h, "endpoint", "fluxo", "método")
        scen_i = _header_index(h, "cenário", "cenarios")
        file_i = _header_index(h, "arquivo teste", "arquivo")
        endpoint = _cell(cells, endpoint_i, cells[0])
        detail = _cell(cells, scen_i)
        scenario = f"{endpoint} — {detail}" if detail and detail != endpoint else endpoint
        return {
            "scenario": scenario,
            "business_flow": endpoint,
            "steps_summary": detail or None,
            "file": _clean_file(_cell(cells, file_i)),
            "spec_status": spec_status,
        }

    case_i = _header_index(h, "caso")
    file_i = _header_index(h, "arquivo")
    scenario = _cell(cells, case_i, cells[0])
    file_val = _clean_file(_cell(cells, file_i))
    return {
        "scenario": scenario,
        "business_flow": scenario,
        "file": file_val,
        "spec_status": spec_status,
    }


def extract_table_rows(spec_text: str, section_pattern: str, layer: str = "unit_back") -> list[dict]:
    lines = spec_text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.search(section_pattern, line, re.I):
            start = i + 1
            break
    if start is None:
        return []
    rows: list[dict] = []
    header: list[str] | None = None
    for line in lines[start:]:
        if line.startswith("## ") and not line.startswith("###"):
            break
        if line.startswith("### ") and not re.search(section_pattern, line, re.I):
            break
        if not line.startswith("|") or "---" in line:
            continue
        cells = _split_table_cells(line)
        if not cells:
            continue
        first = cells[0].lower()
        if first in ("caso", "endpoint", "fluxo", "fluxo de negócio", "método", "endpoint / fluxo"):
            header = cells
            continue
        if header is None:
            continue
        row = _row_from_header(header, cells, layer)
        if row and row.get("scenario"):
            rows.append(row)
    return rows


def parse_spec(req_id: str) -> dict:
    path = find_spec_path(req_id)
    if not path:
        return {"exists": False, "path": None, "status": "missing"}
    text = path.read_text(encoding="utf-8")
    meta = parse_frontmatter(text)
    required = merge_required_layers(parse_required_layers(text))
    cases: dict[str, list] = {}
    for layer, pat in TABLE_SECTIONS.items():
        cases[layer] = extract_table_rows(text, pat, layer)
    cases["contract"] = []
    return {
        "exists": True,
        "path": str(path.relative_to(_CTX["root"])),
        "status": meta.get("status", "draft"),
        "req_kind": meta.get("req_kind", "functional"),
        "critical_flow": bool(meta.get("critical_flow")),
        "required_layers": required,
        "cases": cases,
    }


def extract_req_ids_from_text(text: str) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for m in REQ_TAG_RE.finditer(text or ""):
        rid = normalize_req_id(m.group(0))
        if rid not in seen:
            seen.add(rid)
            out.append(rid)
    return out


def _norm_path(path: str | None) -> str | None:
    if not path:
        return None
    return path.replace("\\", "/").lstrip("./")


def load_manifest_overrides() -> list[dict]:
    data = load_yaml(_CTX["manifest"])
    overrides = data.get("overrides") or []
    return overrides if isinstance(overrides, list) else []


def build_req_trace_map() -> dict:
    """Mapa file/scenario → req_ids a partir das specs + quality-manifest.yaml."""
    by_file: dict[str, dict] = {}
    by_scenario: dict[tuple[str, str], list[str]] = {}

    def add_file(fp: str | None, req_id: str, layer: str, scenario: str) -> None:
        fp = _norm_path(fp)
        if not fp:
            return
        entry = by_file.setdefault(fp, {"req_ids": [], "layer": layer, "scenarios": []})
        if req_id not in entry["req_ids"]:
            entry["req_ids"].append(req_id)
        if scenario and scenario not in entry["scenarios"]:
            entry["scenarios"].append(scenario)

    def add_scenario(layer: str, scenario: str, req_id: str) -> None:
        key = (layer, scenario)
        ids = by_scenario.setdefault(key, [])
        if req_id not in ids:
            ids.append(req_id)

    for br in parse_backlog():
        req_id = br["req_id"]
        spec = parse_spec(req_id)
        if not spec.get("exists"):
            continue
        for layer, rows in (spec.get("cases") or {}).items():
            layer = normalize_layer(layer)
            if layer != "integration" and layer not in PANEL_LAYERS:
                continue
            for row in rows:
                scenario = row.get("scenario") or ""
                add_file(row.get("file"), req_id, layer, scenario)
                add_scenario(layer, scenario, req_id)

    for ov in load_manifest_overrides():
        if not isinstance(ov, dict):
            continue
        req_ids = ov.get("req_ids") or []
        layer = normalize_layer(ov.get("layer") or "unknown")
        if ov.get("file"):
            add_file(ov["file"], req_ids[0] if req_ids else "REQ-???", layer, ov.get("scenario") or "")
            for rid in req_ids:
                entry = by_file.setdefault(_norm_path(ov["file"]) or "", {"req_ids": [], "layer": layer, "scenarios": []})
                for r in req_ids:
                    if r not in entry["req_ids"]:
                        entry["req_ids"].append(r)
        if ov.get("scenario"):
            for rid in req_ids:
                add_scenario(layer, ov["scenario"], rid)

    return {"by_file": by_file, "by_scenario": {f"{k[0]}::{k[1]}": v for k, v in by_scenario.items()}}


def resolve_req_ids_for_test(
    layer: str,
    file_hint: str | None,
    scenario: str | None,
    name: str,
    trace_map: dict,
) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()

    def push(raw: str) -> None:
        if raw and raw not in seen:
            seen.add(raw)
            ids.append(raw)

    for rid in extract_req_ids_from_text(name):
        push(rid)
    for rid in extract_req_ids_from_text(scenario or ""):
        push(rid)

    layer = normalize_layer(layer)
    by_file = trace_map.get("by_file") or {}
    fp = _norm_path(file_hint)
    if fp:
        for key, entry in by_file.items():
            if fp == key or fp.endswith(key) or key.endswith(fp):
                for rid in entry.get("req_ids") or []:
                    push(rid)

    by_scenario = trace_map.get("by_scenario") or {}
    if scenario:
        for key, rids in by_scenario.items():
            if key.startswith(f"{layer}::") and scenario in key:
                for rid in rids:
                    push(rid)
        direct = by_scenario.get(f"{layer}::{scenario}")
        if direct:
            for rid in direct:
                push(rid)

    return ids


def iter_plan_cases(req_filter: str | None = None) -> list[dict]:
    """Todos os casos do plano TDD (para scaffold e validação)."""
    out: list[dict] = []
    for br in parse_backlog():
        req_id = br["req_id"]
        if req_filter and req_id != req_filter:
            continue
        spec = parse_spec(req_id)
        if not spec.get("exists"):
            continue
        required = merge_required_layers(spec.get("required_layers") or {})
        for layer in PANEL_LAYERS:
            if not required.get(layer):
                continue
            for row in (spec.get("cases") or {}).get(layer, []):
                out.append(
                    {
                        "req_id": req_id,
                        "req_title": br.get("title"),
                        "layer": layer,
                        "layer_label": LAYER_LABELS.get(layer, layer),
                        **row,
                    }
                )
    return out


def validate_spec_plans(*, strict: bool = False, approved_only: bool = True) -> list[dict]:
    """Valida coerência camadas marcadas ↔ plano TDD."""
    issues: list[dict] = []
    for br in parse_backlog():
        req_id = br["req_id"]
        spec = parse_spec(req_id)
        if not spec.get("exists"):
            if approved_only:
                continue
            issues.append({"level": "error", "req_id": req_id, "message": "spec ausente"})
            continue
        if approved_only and spec.get("status") != "approved":
            continue
        required = merge_required_layers(spec.get("required_layers") or {})
        for layer in PANEL_LAYERS:
            if not required.get(layer):
                continue
            cases = (spec.get("cases") or {}).get(layer, [])
            label = LAYER_LABELS.get(layer, layer)
            if not cases:
                issues.append(
                    {
                        "level": "error",
                        "req_id": req_id,
                        "layer": layer,
                        "message": f"camada [{label}] marcada mas plano TDD vazio",
                    }
                )
                continue
            if strict and layer in LAYERS_NEED_FILE:
                for row in cases:
                    if row.get("spec_status") in ("n/a",):
                        continue
                    if not row.get("file"):
                        issues.append(
                            {
                                "level": "error",
                                "req_id": req_id,
                                "layer": layer,
                                "scenario": row.get("scenario"),
                                "message": f"sem 'Arquivo teste' na spec ({label})",
                            }
                        )
    return issues
