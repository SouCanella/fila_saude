#!/usr/bin/env python3
"""Resolve próximo passo do funil Modelo → prompt copiável para IA/hub."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "scripts"))
from modelo_ids import find_req_ids  # noqa: E402


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


def parse_cards(cards_dir: Path) -> list[dict]:
    out = []
    if not cards_dir.exists():
        return out
    for p in sorted(cards_dir.glob("CARD-*.md")):
        text = p.read_text(encoding="utf-8")
        meta = load_yaml_from_frontmatter(text)
        status = (meta.get("status") or "open").lower()
        out.append(
            {
                "id": meta.get("id") or p.stem,
                "status": status,
                "phase": meta.get("phase"),
                "title": meta.get("title") or p.stem,
                "path": str(p),
            }
        )
    return out


def load_yaml_from_frontmatter(text: str) -> dict:
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


def first_pending_bootstrap_section(cfg: dict) -> str | None:
    sections = (cfg.get("bootstrap") or {}).get("sections") or {}
    for key, val in sections.items():
        if val not in ("complete", "done", "skipped"):
            return key.replace("_", " ").upper()
    return None


def parse_spec_status(specs_dir: Path, req_id: str) -> str | None:
    if not specs_dir.exists():
        return None
    for p in specs_dir.glob(f"{req_id}*.md"):
        meta = load_yaml_from_frontmatter(p.read_text(encoding="utf-8"))
        return meta.get("status")
    return None


def card_req_ids(card_path: Path) -> list[str]:
    text = card_path.read_text(encoding="utf-8")
    return find_req_ids(text)


def load_module_json(root: Path, data_dir: Path | None, name: str) -> dict:
    candidates: list[Path] = []
    if data_dir:
        candidates.append(data_dir / f"{name}.data.json")
    candidates.append(root / "docs/meta/project-hub/data" / f"{name}.data.json")
    for path in candidates:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
    return {}


def check_hub_delivery_gates(root: Path, cfg: dict, data_dir: Path | None, req_ids: list[str] | None = None) -> dict | None:
    """Bloqueia entrega TDD se security/design/a11y tiverem gaps críticos."""
    project = cfg.get("project") or {}
    has_frontend = project.get("has_frontend") is True
    req_ids = req_ids or []

    security = load_module_json(root, data_dir, "security")
    sec_rep = security.get("report") or {}
    sec_gaps = security.get("gaps") or []
    if sec_gaps:
        card_gaps = [g for g in sec_gaps if g.get("req_id") in req_ids] if req_ids else sec_gaps
        relevant = card_gaps or sec_gaps
        if not sec_rep.get("global_checklist_complete") or any(g.get("sensitive") for g in relevant):
            blockers = [
                (g.get("gap") or g.get("label") or f"{g.get('req_id')} gap")
                for g in relevant[:4]
            ]
            return {
                "phase": "delivery",
                "label": "Fechar gaps de segurança",
                "prompt": (
                    "Antes de implementar ou fechar o card, resolva lacunas no hub (#security): "
                    "checklist global em docs/security/security-checklist.md e threat model "
                    "para REQs sensíveis. Depois make hub-build."
                ),
                "skill": "feature-delivery",
                "blockers": blockers,
                "hub_hash": "#security",
            }

    if has_frontend:
        design = load_module_json(root, data_dir, "design")
        des_rep = design.get("report") or {}
        if not des_rep.get("ready_for_ui_impl"):
            des_gaps = [g.get("label", "") for g in (design.get("gaps") or [])[:3]]
            return {
                "phase": "delivery",
                "label": "Design não pronto para UI",
                "prompt": (
                    "Complete mocks HTML e APPROVAL.md; aprove design.status no config "
                    "antes de implementar framework UI. Ver módulo #design no hub."
                ),
                "skill": "project-bootstrap",
                "blockers": des_gaps or [f"Status: {design.get('design_status', 'draft')}"],
                "hub_hash": "#design",
            }

        a11y = load_module_json(root, data_dir, "a11y")
        a11y_rep = a11y.get("report") or {}
        ok = a11y_rep.get("checklist_ok", 0)
        total = a11y_rep.get("checklist_total") or 0
        if total and ok < total:
            return {
                "phase": "delivery",
                "label": "Checklist a11y incompleto",
                "prompt": (
                    "Complete a seção Acessibilidade em design-references/APPROVAL.md "
                    "e valide mocks por tela. Ver módulo #a11y no hub."
                ),
                "skill": "project-bootstrap",
                "blockers": [f"Checklist a11y: {ok}/{total}"],
                "hub_hash": "#a11y",
            }

    return None


def parse_retro_index(root: Path) -> dict[str, str]:
    for rel in ("docs/meta/retrospectives/index.md",):
        path = root / rel
        if path.exists():
            break
    else:
        return {}
    status_by_phase: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line or "Fase" in line:
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if parts and parts[0].startswith("FASE-"):
            status_by_phase[parts[0]] = parts[1].lower() if len(parts) > 1 else "pending"
    return status_by_phase


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
        if parts and parts[0].startswith("FASE-"):
            phases.append({"id": parts[0], "label": parts[1] if len(parts) > 1 else parts[0]})
    return phases


def phase_cards_all_done(cards: list[dict], phase_id: str) -> bool:
    phase_cards = [c for c in cards if c.get("phase") == phase_id]
    return bool(phase_cards) and all(c["status"] == "done" for c in phase_cards)


def pending_retro_phase(cards: list[dict], root: Path) -> str | None:
    retro_index = parse_retro_index(root)
    for mp in parse_mvp_phases(root):
        pid = mp["id"]
        if phase_cards_all_done(cards, pid) and retro_index.get(pid, "pending") == "pending":
            return pid
    return None


def resolve_next_step(
    root: Path,
    config_path: Path | None = None,
    cards_dir: Path | None = None,
    specs_dir: Path | None = None,
    data_dir: Path | None = None,
) -> dict:
    root = root.resolve()
    config_path = config_path or root / "project.config.yaml"
    cards_dir = cards_dir or root / "docs/tracking/cards"
    specs_dir = specs_dir or root / "docs/specs"
    if data_dir is None:
        candidate = root / "docs/meta/project-hub/data"
        data_dir = candidate if candidate.is_dir() else None
    cfg = load_yaml(config_path)
    template = cfg.get("template") or {}

    discovery = cfg.get("discovery") or {}
    bootstrap = cfg.get("bootstrap") or {}
    mvp_planning = cfg.get("mvp_planning") or {}
    project = cfg.get("project") or {}
    design = cfg.get("design") or {}
    has_frontend = project.get("has_frontend") is True
    project_name = project.get("name")
    project_name_empty = project_name is None or project_name == "" or project_name == "null"

    if (
        template.get("is_upstream") is True
        and template.get("sibling_spawn_required") is True
        and not template.get("upstream_dev_mode")
    ):
        return {
            "phase": "spawn",
            "label": "Criar pasta irmã do produto",
            "prompt": (
                'Fase −1: na pasta Modelo upstream execute make create-project NAME="<nome do produto>" GIT_INIT=1; '
                "abra a pasta irmã no Cursor (ver docs/operations/spawn-project.md); "
                "inicie project-discovery só na irmã (.modelo-product-workspace)."
            ),
            "skill": "project-discovery",
            "blockers": ["Produto ainda não foi criado como pasta irmã do Modelo"],
            "hub_hash": "#overview",
        }

    if (
        template.get("is_upstream") is True
        and template.get("sibling_spawn_required") is True
        and template.get("upstream_dev_mode") is True
        and discovery.get("status") != "complete"
        and not discovery.get("skipped")
        and project_name_empty
    ):
        return {
            "phase": "spawn",
            "label": "Spawn (informativo) — template ou produto novo?",
            "prompt": (
                "Evoluindo o template Modelo (CARD-Hub, scripts)? Ignore e siga discovery aqui "
                "(upstream_dev_mode ativo). Produto novo? make create-project NAME=\"<nome>\" nesta pasta "
                "Modelo e abra a pasta irmã no Cursor — docs/operations/spawn-project.md."
            ),
            "skill": "project-discovery",
            "blockers": [],
            "hub_hash": "#overview",
            "informative": True,
        }

    if discovery.get("status") != "complete" and not discovery.get("skipped"):
        return {
            "phase": "discovery",
            "label": "Concluir descoberta leve",
            "prompt": (
                "Execute a skill project-discovery: refine visão e escopo MVP, "
                "preencha docs/discovery/vision-review.md e confirme o checklist humano "
                "para marcar discovery.status: complete em project.config.yaml."
            ),
            "skill": "project-discovery",
            "blockers": [],
            "hub_hash": "#overview",
        }

    if bootstrap.get("status") != "complete":
        pending = first_pending_bootstrap_section(cfg)
        hint = f" (bloco {pending} pendente)" if pending else ""
        return {
            "phase": "bootstrap",
            "label": "Continuar bootstrap" + hint,
            "prompt": (
                f"Execute a skill project-bootstrap{hint}; use docs/discovery/bootstrap-hints.md "
                "e preencha project.config.yaml até bootstrap.status: complete."
            ),
            "skill": "project-bootstrap",
            "blockers": [],
            "hub_hash": "#design",
        }

    if has_frontend and design.get("status") != "approved":
        return {
            "phase": "bootstrap",
            "label": "Aprovar padrão visual",
            "prompt": (
                "Revise os mocks HTML em design-references/, complete design-references/APPROVAL.md "
                "(checklist + a11y) e aprove o padrão visual (design.status: approved)."
            ),
            "skill": "project-bootstrap",
            "blockers": [],
            "hub_hash": "#design",
        }

    if mvp_planning.get("status") != "complete":
        return {
            "phase": "mvp_planning",
            "label": "Planejar MVP executável",
            "prompt": (
                "Execute a skill project-mvp-planning: defina fases, REQs no backlog, "
                "cards MD e requirements-review.md até mvp_planning.status: complete."
            ),
            "skill": "project-mvp-planning",
            "blockers": [],
            "hub_hash": "#overview",
        }

    cards = parse_cards(cards_dir)
    retro_phase = pending_retro_phase(cards, root)
    if retro_phase:
        return {
            "phase": "retro",
            "label": f"Retrospectiva {retro_phase}",
            "prompt": (
                f"Execute skill phase-retrospective para {retro_phase}; "
                "documente em docs/meta/retrospectives/ e atualize o índice antes de abrir o próximo CARD."
            ),
            "skill": "phase-retrospective",
            "blockers": [f"Retro {retro_phase} pendente"],
            "hub_hash": "#overview",
        }

    in_progress = [c for c in cards if c["status"] == "in_progress"]
    if in_progress:
        card = in_progress[0]
        card_path = Path(card["path"])
        req_ids = card_req_ids(card_path)
        blockers = []
        for rid in req_ids:
            st = parse_spec_status(specs_dir, rid)
            if st and st != "approved":
                blockers.append(f"Spec {rid} está {st} (precisa approved)")
        if blockers:
            return {
                "phase": "delivery",
                "label": f"Aprovar specs do {card['id']}",
                "prompt": (
                    f"Revise e aprove as specs pendentes do {card['id']} "
                    f"({', '.join(req_ids) or 'REQs do card'}) antes de implementar código."
                ),
                "skill": "card-tracking",
                "blockers": blockers,
                "hub_hash": "#quality",
            }
        gate = check_hub_delivery_gates(root, cfg, data_dir, req_ids)
        if gate:
            return gate
        req_hint = req_ids[0] if req_ids else "REQ do card"
        return {
            "phase": "delivery",
            "label": f"Implementar {card['id']}",
            "prompt": (
                f"Implemente {card['id']} com skill feature-delivery (TDD): "
                f"comece por {req_hint}, valide plano com make quality-validate-specs "
                "e feche gaps no hub (#quality) antes de fechar o card."
            ),
            "skill": "feature-delivery",
            "blockers": [],
            "hub_hash": "#quality",
        }

    open_cards = [c for c in cards if c["status"] in ("open", "ready", "todo", "pending")]
    if open_cards:
        nxt = open_cards[0]
        card_path = Path(nxt["path"])
        if not card_path.is_absolute():
            card_path = root / card_path
        req_ids = card_req_ids(card_path) if card_path.exists() else []
        gate = check_hub_delivery_gates(root, cfg, data_dir, req_ids)
        if gate:
            gate["label"] = f"Pré-requisitos para {nxt['id']}"
            return gate
        return {
            "phase": "delivery",
            "label": f"Abrir {nxt['id']}",
            "prompt": (
                f"Abra {nxt['id']} como in_progress (skill card-tracking) conforme "
                "docs/planning/cards-backlog.md e confirme specs approved dos REQs vinculados."
            ),
            "skill": "card-tracking",
            "blockers": [],
            "hub_hash": "#process",
        }

    if cards and all(c["status"] == "done" for c in cards):
        return {
            "phase": "retro",
            "label": "Retrospectiva de fase",
            "prompt": (
                "Execute skill phase-retrospective para a fase concluída; "
                "documente em docs/meta/retrospectives/ e planeje a próxima fase."
            ),
            "skill": "phase-retrospective",
            "blockers": [],
            "hub_hash": "#overview",
        }

    return {
        "phase": "delivery",
        "label": "Iniciar entrega",
        "prompt": (
            "Crie ou abra o primeiro CARD do MVP (card-tracking), "
            "garanta spec approved e implemente com feature-delivery + TDD."
        ),
        "skill": "card-tracking",
        "blockers": [],
        "hub_hash": "#overview",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--config", type=Path)
    p.add_argument("--cards-dir", type=Path)
    p.add_argument("--specs-dir", type=Path)
    p.add_argument("--data-dir", type=Path)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    result = resolve_next_step(args.root, args.config, args.cards_dir, args.specs_dir, args.data_dir)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result.get("prompt", ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
