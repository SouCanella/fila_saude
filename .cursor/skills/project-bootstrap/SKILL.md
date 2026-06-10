---
name: project-bootstrap
description: Configures a new project from the Modelo template via questionnaire blocks A-N. Use when starting a new project, bootstrap, inicializar projeto, configurar stack, or project.config.yaml is incomplete.
---

# Project bootstrap

## When to use

- `discovery.status == complete` OR `discovery.skipped == true`
- `project.config.yaml` → `bootstrap.status != complete`
- User says: bootstrap, configurar stack (after discovery)

## Before block A

If `template.is_upstream: true` and not `template.upstream_dev_mode`: stop — [spawn-project.md](../../docs/operations/spawn-project.md) — **make create-project** first; bootstrap and **design-references/screens/** mocks (bloco H) only in the **sibling** folder.

If `discovery.status == complete` (not skipped), read:

- `docs/discovery/product-discovery.md`
- `docs/discovery/bootstrap-hints.md`
- `docs/backlog/mvp-backlog.md`
- `docs/discovery/requirements-review.md` (must be human-confirmed)

**Confirm/refine** drafts in blocks A and B instead of cold-start questions.

Block **J**: align REQ prefix with backlog; configure `tracking.cards` provider; refine cards from discovery.

## Instructions

1. Read `project.config.yaml` and `docs/00-getting-started.md`.
2. Run questionnaire in [questionnaire.md](questionnaire.md) **block by block** (5–8 questions per turn).
3. After each block: update config section to `complete` and generate listed files.
4. Do **not** implement product code until bootstrap complete.
5. Block H (if `has_frontend`): create mocked HTML in `design-references/screens/` (align with backlog screens).
6. At end: set `bootstrap.status: complete`, `bootstrap.completed_at`.
7. Ask user for learnings → `docs/meta/improving-the-template.md`.
8. Milestones `bootstrap` (+ `design_mock` / `design_approved` if block H + approval); **process-metrics** rounds each turn; `build-process-metrics.sh`.

## Block order

A → B → C → D → E → F → G → H (if front) → I → J → K → L → M → N

## Artifacts per block

See [questionnaire.md](questionnaire.md).
