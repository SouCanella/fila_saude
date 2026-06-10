#!/usr/bin/env bash
# Copia e reescreve embeds Process/Quality para o hub (fonte única).
set -euo pipefail
TEMPLATE="$(cd "$(dirname "$0")/.." && pwd)"
HUB="${1:-${TEMPLATE}/docs/meta/project-hub}"
META_TEMPLATE="${TEMPLATE}/docs/meta"

SRC_PM="${META_TEMPLATE}/process-metrics"
SRC_QH="${META_TEMPLATE}/quality-health"
DST_PM="${HUB}/modules/process"
DST_QH="${HUB}/modules/quality"

mkdir -p "$DST_PM" "$DST_QH"

cp "${SRC_PM}/process-metrics.css" "${DST_PM}/process.css"
cp "${SRC_QH}/quality-health.css" "${DST_QH}/quality.css"
sed 's|fetch("process-metrics.data.json")|fetch("data/process.data.json")|g' \
  "${SRC_PM}/process-metrics.js" > "${DST_PM}/process.js"
sed 's|quality-health.data.json|data/quality.data.json|g' \
  "${SRC_QH}/quality-health.js" > "${DST_QH}/quality.js"

echo "OK: hub embeds → ${HUB}/modules/{process,quality}"
