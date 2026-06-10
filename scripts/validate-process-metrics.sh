#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
YAML="${ROOT}/docs/meta/process-timeline.yaml"
JSON="${ROOT}/docs/meta/process-metrics/process-metrics.data.json"
STRICT="${PROCESS_METRICS_STRICT:-0}"
WARN=0
ERR=0

warn() { echo "AVISO: $1"; WARN=1; }
fail() { echo "ERRO: $1"; ERR=1; }

if [[ ! -f "$YAML" ]]; then
  if [[ "$STRICT" == "1" ]]; then
    fail "docs/meta/process-timeline.yaml ausente"
  else
    warn "docs/meta/process-timeline.yaml ausente"
    exit 0
  fi
fi

if grep -q "needs_review: true" "$YAML" 2>/dev/null; then
  warn "existem rodadas com needs_review: true — revisar no painel ou corrigir YAML"
fi

if [[ ! -f "$JSON" ]]; then
  if [[ "$STRICT" == "1" ]]; then
    fail "process-metrics.data.json ausente — rode ./scripts/build-process-metrics.sh"
  else
    warn "process-metrics.data.json ausente — rode ./scripts/build-process-metrics.sh"
  fi
else
  if [[ "$YAML" -nt "$JSON" ]]; then
    msg="YAML mais novo que JSON — rode ./scripts/build-process-metrics.sh"
    if [[ "$STRICT" == "1" ]]; then
      fail "$msg"
    else
      warn "$msg"
    fi
  fi
fi

if grep -A6 "phase_delivery_end" "$YAML" 2>/dev/null | grep -q "ended_at: null"; then
  warn "marco phase_delivery_end com ended_at null"
fi

if [[ $ERR -eq 1 ]]; then
  exit 1
fi

if [[ $WARN -eq 0 ]]; then
  echo "OK: métricas de processo"
fi
exit 0
