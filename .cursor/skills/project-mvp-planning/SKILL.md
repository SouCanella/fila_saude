---
name: project-mvp-planning
description: Executable MVP planning after bootstrap and design approval — phases, REQs, cards, requirements review. Use when mvp_planning.status is pending and bootstrap is complete.
---

# Project MVP planning (fase 2)

## When to use

- Workspace de **produto** (`.modelo-product-workspace` ou `template.is_upstream: false`) — não planejar MVP no Modelo upstream sem spawn
- `bootstrap.status: complete`
- If `has_frontend: true` → `design.status: approved`
- `mvp_planning.status != complete`
- User asks to plan MVP, create cards/REQs, validate traceability

## Do not use

- Before bootstrap complete
- Before design approved (when front exists) — finish mocks first
- For product code or feature-delivery

## Instructions

1. Read [questionnaire-mvp-planning.md](questionnaire-mvp-planning.md), [docs/00-project-lifecycle.md](../../docs/00-project-lifecycle.md), [req-slicing.md](../../docs/specs/req-slicing.md).
2. **Order:** Fases → REQs → Cards (1 card : N reqs) → MD em `docs/tracking/cards/`.
3. Run [req-validation-checklist.md](../../docs/specs/req-validation-checklist.md) → `requirements-review.md`.
4. **Gate:** every REQ in backlog in ≥1 card before `mvp_planning.status: complete`.
5. Human confirms `requirements-review.md` → set `mvp_planning.review_confirmed_at`, `mvp_planning.completed_at`, `status: complete`.
6. `./scripts/validate-planning.sh`
7. Milestones `mvp_planning_start` / `mvp_planning_end` + **process-metrics** round; `build-process-metrics.sh` (habilita projeções **(est.)** no painel).
8. Opcional: **process-benchmark** — `export-process-benchmark.sh` + `aggregate-process-benchmarks.sh`.

## Artifacts

See [questionnaire-mvp-planning.md](questionnaire-mvp-planning.md).

## Response format (end of planning)

- Fases (FASE-1…)
- Cards (CARD-001…) with linked REQs
- Review status (ok / gaps)
- Next step: open CARD + specs + **feature-delivery**
- Lembrete: previsões no painel são **estatísticas**, não datas de negócio
