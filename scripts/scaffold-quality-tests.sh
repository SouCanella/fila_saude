#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEMO="${ROOT}/examples/quality-health-demo"
DRY="${1:-}"
exec python3 "${ROOT}/scripts/scaffold_quality_tests.py" \
  --root "$DEMO" \
  --backlog "${DEMO}/backlog/mvp-backlog.md" \
  --specs-dir "${DEMO}/specs" \
  ${DRY:+--dry-run}
