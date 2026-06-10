---
name: phase-retrospective
description: Short retrospective after all cards in a FASE are done. Documents process learnings or explicit skip. Soft gate — does not block next phase. Use when closing last card of a phase, user asks for retro, or validate-phase-retros warns.
---

# Phase retrospective

## When to use

- All cards with `phase: FASE-X` are `done` in `docs/planning/cards-backlog.md` and card MD files
- User says: retro, retrospectiva, lições da fase, FASE-X concluída
- After **card-tracking** closes the last card of a phase
- `./scripts/validate-phase-retros.sh` reports missing retro for a completed phase

## Prerequisites

- Read `docs/planning/mvp-phases.md`, `docs/planning/cards-backlog.md`, card MD under `docs/tracking/cards/`
- Confirm every card mapped to `FASE-X` has `status: done` (or `cancelled` with note — do not treat cancelled as delivery without human confirmation)

## Instructions

1. Identify `FASE-X` and list cards delivered in this phase.
2. If any card is still `open` or `in_progress`, **stop** — report which cards remain; do not start retro yet.
3. Check `docs/meta/retrospectives/index.md` — if `FASE-X` already `completed` or `skipped`, offer to update only if user asks.
4. Ask **one turn** of short questions (from template `_template-fase-retro.md` §1–6). Do not run a long questionnaire across many turns unless user asks.
5. On answers:
   - Create or update `docs/meta/retrospectives/FASE-X-retro.md` from `_template-fase-retro.md`
   - Set frontmatter: `status: completed`, `completed_at`, `participants`, `cards_delivered`
   - Update `index.md` row for `FASE-X`
6. If user **skips** retro:
   - Create `FASE-X-retro.md` with `status: skipped`, `skipped_at`, `skipped_reason` (user's words)
   - Update `index.md` with `skipped` and brief note
   - Do **not** block opening cards of the next phase
7. If items apply to the **Modelo template** (not just this product), suggest bullets for `docs/meta/improving-the-template.md` — user decides whether to copy.
8. Optionally suggest updating `mvp-phases.md` retro column (`completed` / `skipped` / `pending`) if the table exists.
9. Milestone `phase_retro` for `FASE-X`; **process-metrics** round; suggest human read time split on `docs/meta/process-metrics/index.html`; `build-process-metrics.sh`.

## Soft gate

- **Warn strongly** when opening a card in `FASE-(X+1)` if `FASE-X` has all cards `done` but no `completed` or `skipped` in `index.md`
- **Never** refuse feature-delivery or card open solely for missing retro

## Response format

- FASE-X and card list
- Retro status: completed | skipped
- Files updated (`FASE-X-retro.md`, `index.md`)
- One recommended action for next phase
- Modelo upstream items (if any)
