---
name: card-tracking
description: Open, update, and close work cards (CARD-XXX). Mandatory MD in repo; optional external sync (GitHub, Jira, Kanbanize, Azure). Use when opening card, implementing CARD, closing card, or syncing issue tracker.
---

# Card tracking

## When to use

- Open / update / close **CARD-XXX**
- Implement work from a card (before feature-delivery)
- Sync external provider configured in `tracking.cards`

## Prerequisites

- `tracking.cards.required: true` (always in Modelo)
- `mvp_planning.status: complete` before opening card `in_progress`
- Card exists in `docs/planning/cards-backlog.md` + `docs/tracking/cards/CARD-XXX.md`
- **Implement:** card `in_progress` + all linked REQ specs `approved`

## Open card

1. Read card MD + linked REQs
2. Verify all `req_ids` specs are `approved`
3. Set card `status: in_progress`; set `opened_at` (ISO); suggest branch `feature/CARD-XXX-slug`
4. Update `cards-backlog.md` index
5. Set `process_metrics.active_context` (card_id, phase, `implementation`); milestone `phase_delivery_start` if first card of phase; **process-metrics**
6. If external provider: create issue/board item; set `external_id`, `external_url` on card MD
7. See [issue-cards.md](../../docs/operations/issue-cards.md) per provider

## Update card

- Link PR, assignee, notes
- Sync external status if configured

## Close card

1. All linked REQs meet DoD (feature-delivery done for each)
2. Card `status: done`; set `done_at` (ISO)
3. Update matrix, delivery-log (CARD-centric entry)
4. Close external issue if `external_url` set
5. **process-metrics:** round + if last card of phase → milestone `phase_delivery_end`; `./scripts/build-process-metrics.sh`
6. **quality-health:** `make quality-validate-specs` + `make quality-build` — gaps verdes ou justificativa em `tech-debt.md`
7. **Project Hub:** `make hub-build` — atualiza funil de fases, entregas e atividade no Overview
8. Se último card do MVP: sugerir **process-benchmark** (export + índice de benchmarks)
9. **Phase retro hook:** read card `phase` (frontmatter). If every card in the same `FASE-X` is now `done` (status no card MD), this was the **last delivery** of the phase → suggest skill **phase-retrospective** (do not block card close). See [docs/meta/retrospectives/README.md](../../docs/meta/retrospectives/README.md).

## Providers

| provider | Action |
|----------|--------|
| `markdown` | MD only |
| `github_issues` | `gh issue` + MD mirror; helper: `./scripts/sync-card-github.sh {open|close|comment} CARD-XXX [--dry-run]` — `open` atualiza `external_url` no frontmatter |
| `jira` / `kanbanize` / `azure_devops` | API + `.env`; update MD |

**MD is always canonical** (`mirror_in_repo: true`).

## Response format

- Card ID and status
- REQs affected
- External sync result (if any)
- Files updated
