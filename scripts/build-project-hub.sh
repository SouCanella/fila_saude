#!/usr/bin/env bash
set -euo pipefail
TEMPLATE="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="${1:-$TEMPLATE}"
SCRIPTS="${TEMPLATE}/scripts"

HUB="${PROJECT}/docs/meta/project-hub"
DATA="${HUB}/data"
META_TEMPLATE="${TEMPLATE}/docs/meta"

if [[ "$PROJECT" == "$TEMPLATE" ]]; then
  META_OUT="${META_TEMPLATE}"
else
  META_OUT="${PROJECT}/docs/meta"
  mkdir -p "${META_OUT}/process-metrics" "${META_OUT}/quality-health"
fi

CONFIG="${PROJECT}/project.config.demo.yaml"
[[ -f "$CONFIG" ]] || CONFIG="${PROJECT}/project.config.yaml"

BACKLOG="${PROJECT}/backlog/mvp-backlog.md"
[[ -f "$BACKLOG" ]] || BACKLOG="${PROJECT}/docs/backlog/mvp-backlog.md"

MATRIX="${PROJECT}/traceability-matrix.md"
[[ -f "$MATRIX" ]] || MATRIX="${PROJECT}/docs/traceability-matrix.md"

SPECS="${PROJECT}/specs"
[[ -d "$SPECS" ]] || SPECS="${PROJECT}/docs/specs"

TIMELINE="${PROJECT}/docs/meta/process-timeline.yaml"
[[ -f "$TIMELINE" ]] || TIMELINE="${META_TEMPLATE}/process-timeline.yaml"

CARDS_DIR="${PROJECT}/tracking/cards"
[[ -d "$CARDS_DIR" ]] || CARDS_DIR="${PROJECT}/docs/tracking/cards"

CARDS_BACKLOG="${PROJECT}/planning/cards-backlog.md"
[[ -f "$CARDS_BACKLOG" ]] || CARDS_BACKLOG="${PROJECT}/docs/planning/cards-backlog.md"

MVP_PHASES="${PROJECT}/planning/mvp-phases.md"
[[ -f "$MVP_PHASES" ]] || MVP_PHASES="${PROJECT}/docs/planning/mvp-phases.md"

LAST_RUN="${PROJECT}/quality-runs/manual.yaml"
[[ -f "$LAST_RUN" ]] || LAST_RUN="${META_TEMPLATE}/quality-runs/manual.yaml"

# Showcase (REQ-001/004) só em examples/project-hub-demo — template virgem usa backlog/specs reais.
mkdir -p "$DATA"

python3 "${SCRIPTS}/build_process_metrics.py" \
  --yaml "$TIMELINE" \
  --json "${DATA}/process.data.json" \
  --config "$CONFIG" \
  --cards-backlog "$CARDS_BACKLOG" \
  --mvp-phases "$MVP_PHASES" \
  --cards-dir "$CARDS_DIR"

cp "${DATA}/process.data.json" "${META_OUT}/process-metrics/process-metrics.data.json"

python3 "${SCRIPTS}/build_quality_health.py" \
  --root "$PROJECT" \
  --config "$CONFIG" \
  --backlog "$BACKLOG" \
  --matrix "$MATRIX" \
  --specs-dir "$SPECS" \
  --last-run-manual "$LAST_RUN" \
  --json "${DATA}/quality.data.json"

cp "${DATA}/quality.data.json" "${META_OUT}/quality-health/quality-health.data.json"

python3 "${SCRIPTS}/build_security_health.py" \
  --root "$PROJECT" --config "$CONFIG" --backlog "$BACKLOG" --specs-dir "$SPECS" \
  --json "${DATA}/security.data.json"

python3 "${SCRIPTS}/build_accessibility_health.py" \
  --root "$PROJECT" --config "$CONFIG" \
  --json "${DATA}/a11y.data.json"

python3 "${SCRIPTS}/build_design_readiness.py" \
  --root "$PROJECT" --config "$CONFIG" \
  --json "${DATA}/design.data.json"

python3 "${SCRIPTS}/build_delivery_history.py" \
  --root "$PROJECT" --json "${DATA}/delivery.data.json"

python3 "${SCRIPTS}/build_retro_benchmark.py" \
  --root "$PROJECT" --json "${DATA}/learning.data.json"

python3 "${SCRIPTS}/build_tech_debt_health.py" \
  --root "$PROJECT" --json "${DATA}/tech_debt.data.json"

python3 "${SCRIPTS}/build_openapi_health.py" \
  --root "$PROJECT" --config "$CONFIG" --json "${DATA}/openapi.data.json"

python3 "${SCRIPTS}/build_release_health.py" \
  --root "$PROJECT" --config "$CONFIG" --json "${DATA}/release.data.json"

python3 "${SCRIPTS}/build_project_journey.py" \
  --root "$PROJECT" --config "$CONFIG" \
  --cards-dir "$CARDS_DIR" --specs-dir "$SPECS" --backlog "$BACKLOG" \
  --data-dir "$DATA" --json "${DATA}/journey.data.json"

python3 "${SCRIPTS}/build_hub_overview.py" \
  --root "$PROJECT" --data-dir "$DATA" --config "$CONFIG" \
  --cards-dir "$CARDS_DIR" --specs-dir "$SPECS" \
  --json "${DATA}/hub.data.json"

chmod +x "${SCRIPTS}/build-hub-embeds.sh"
"${SCRIPTS}/build-hub-embeds.sh" "$HUB"

echo "OK: ${DATA}/hub.data.json"
