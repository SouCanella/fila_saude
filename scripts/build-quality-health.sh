#!/usr/bin/env bash
# Gera quality-health.data.json — mesmas regras de backlog/specs que build-project-hub.sh
set -euo pipefail
TEMPLATE="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="${1:-$TEMPLATE}"

CONFIG="${PROJECT}/project.config.demo.yaml"
[[ -f "$CONFIG" ]] || CONFIG="${PROJECT}/project.config.yaml"

BACKLOG="${PROJECT}/docs/backlog/mvp-backlog.md"
MATRIX="${PROJECT}/docs/traceability-matrix.md"
SPECS="${PROJECT}/docs/specs"
LAST_RUN="${PROJECT}/docs/meta/quality-runs/manual.yaml"
JSON_OUT="${PROJECT}/docs/meta/quality-health/quality-health.data.json"

# Showcase (REQ-001/004) só em examples/project-hub-demo — template virgem usa backlog/specs reais.

exec python3 "${TEMPLATE}/scripts/build_quality_health.py" \
  --root "$PROJECT" \
  --config "$CONFIG" \
  --backlog "$BACKLOG" \
  --matrix "$MATRIX" \
  --specs-dir "$SPECS" \
  --last-run-manual "$LAST_RUN" \
  --json "$JSON_OUT"
