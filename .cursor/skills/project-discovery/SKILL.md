---
name: project-discovery
description: Light product discovery before bootstrap — vision, MVP scope narrative, stack hints. Use when discovery.status is pending or validating vision only (not full REQ/card planning).
---

# Project discovery (fase 0 — leve)

## When to use

- `discovery.status != complete` and `discovery.skipped != true`
- User describes a new product idea broadly (before bootstrap)
- **Not** for full MVP planning (use **project-mvp-planning** after mocks + bootstrap)

## Instructions

0. **Fase −1 Spawn** ([spawn-project.md](../../docs/operations/spawn-project.md)): se `template.is_upstream: true` e `template.sibling_spawn_required: true` e **não** `template.upstream_dev_mode`:
   - Pergunte só o **nome do produto**.
   - Rode `make create-project NAME="<nome>" GIT_INIT=1` no Modelo upstream.
   - Informe o caminho `../<slug>`; peça **Open Folder** na irmã (`.modelo-product-workspace`).
   - **Pare** — não gravar `docs/discovery/`, `design-references/screens/` nem backlog no upstream.
   - Se já existe `.modelo-product-workspace` ou `template.is_upstream: false`, siga para o passo 1 nesta pasta.
1. Read `project.config.yaml`, [questionnaire-discovery.md](questionnaire-discovery.md), [docs/DISCOVERY.md](../../docs/DISCOVERY.md), [00-project-lifecycle.md](../../docs/00-project-lifecycle.md).
   - If `process_metrics.project_started_at` is null, set it at first turn; milestone `discovery` start (skill **process-metrics**).
2. Conversation **topic by topic** (5–8 questions per turn) — topics 1–6 in questionnaire only.
3. Do **not** implement product code; do **not** complete bootstrap; do **not** require cards/REQs as gate.
4. Optional draft backlog — mark as rascunho, not final.
5. Fill [vision-review.md](../../docs/discovery/vision-review.md) checklist with human.
6. **Gate:** human confirms vision/scope → set `discovery.status: complete`, `discovery.review_confirmed_at`, `discovery.completed_at`.
7. Register milestone `discovery` ended + agent **round** (**process-metrics**); `build-process-metrics.sh`.
8. Run `make hub-build` — funil Fase 0 no Overview reflete conclusão da descoberta.

## Skip discovery

Only if user explicitly says to skip. Set `discovery.skipped: true`, note in `product-discovery.md`, then suggest bootstrap.

## Artifacts (fase 0)

- `docs/discovery/product-discovery.md`
- `docs/discovery/bootstrap-hints.md`
- `docs/discovery/vision-review.md`
- Optional draft: `docs/01-product-vision.md`

## Response format (end of discovery)

- Visão e escopo MVP resumidos
- Próximo passo: **project-bootstrap** (A–N)
- **Não** prometer cards/REQs fechados — isso é fase 2 (**project-mvp-planning**)
