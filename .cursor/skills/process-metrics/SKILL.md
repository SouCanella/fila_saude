---
name: process-metrics
description: Register process time metrics (milestones, sessions, agent rounds) in process-timeline.yaml. Resolve phase/activity context. Transparent 3-line summary. Use after agent turns, session start/end, gates, or correcting metrics.
---

# Process metrics

## When to use

- End of **agent turn** (governance work: discovery, bootstrap, cards, delivery, retro)
- User: "Início sessão", "Fim sessão", "Contexto métricas CARD-XXX"
- User corrects a round or milestone
- After updating gates → register **milestone**
- Before/after `build-process-metrics.sh` when dashboard needed

## Prerequisites

- `process_metrics.enabled: true` in `project.config.yaml`
- Read [`docs/meta/process-metrics.md`](../../docs/meta/process-metrics.md)

## Context resolver (priority)

1. `process_metrics.active_context` in `project.config.yaml`
2. Single card `status: in_progress` → use `phase`, `card_id`, activity `implementation`
3. Active skill mapping:
   - `project-discovery` → `discovery`, `SETUP`
   - `project-bootstrap` → `bootstrap`, `SETUP`
   - `project-mvp-planning` → `planning_review`, `SETUP`
   - `phase-retrospective` → `phase_retro`, card's `FASE-X`
   - `feature-delivery` / `card-tracking` → `implementation` or `spec_refinement`, from card
4. Project gates: discovery incomplete → `discovery`; bootstrap incomplete → `bootstrap`; design not approved + UI → `design_mock`
5. Ambiguous → ask human **or** register with `phase: unknown`, `needs_review: true`

## Register agent round (end of turn)

Append to [`docs/meta/process-timeline.yaml`](../../docs/meta/process-timeline.yaml) `rounds:`:

```yaml
- id: round-YYYY-MM-DDTHH-MM  # unique
  at: <ISO8601 now>
  activity: <resolved>
  phase: <SETUP | FASE-X | unknown>
  card_id: <or null>
  human_active_seconds: <estimate since last round or 0>
  ai_execution_seconds: <estimate turn duration OR ai_minutes_per_round_default * 60>
  idle_before_seconds: <gap from previous round end; if >= idle_threshold_hours*3600, counts as idle>
  source: agent_turn
  needs_review: <true if ambiguous>
```

- Set `updated_at` on timeline file
- Append one line to [`docs/meta/process-metrics-log.md`](../../docs/meta/process-metrics-log.md)
- Run `./scripts/build-process-metrics.sh` (or ask user to run)
- Run `make hub-build` — timeline e funil de fases no Overview
- **Transparency:** reply exactly 3 lines:
  1. What was recorded (id, activity, phase, card)
  2. Human / AI / idle seconds (approx)
  3. Open panel: `make hub-serve` → http://localhost:8090/project-hub/#process (legado: `./scripts/serve-process-metrics.sh`)

## Register milestone

On gate completion (discovery, bootstrap, design approved, **architecture_baseline**, mvp_planning_end, phase delivery start/end, retro):

```yaml
- id: <unique>
  activity: <catalog>
  phase: SETUP | FASE-X
  started_at: ...
  ended_at: ...
```

Sync `process_metrics.project_started_at` on first discovery milestone if null.

## Session start / end

**Start:** append `sessions[]` with `started_at`, resolved activity/phase/card; optionally set `active_context` in config.

**End:** set `ended_at`, optional `human_active_minutes`; clear or keep `active_context` per user choice.

## Set active context

Update `project.config.yaml`:

```yaml
process_metrics:
  active_context:
    activity: implementation
    phase: FASE-1
    card_id: CARD-003
    set_at: <ISO>
```

## Correct entry

User provides round id + fixes → edit YAML, set `needs_review: false`, rebuild JSON, 3-line summary.

## Do not

- Store metrics only under `.cursor/`
- Skip summary after writing
- Block feature-delivery if metrics missing
