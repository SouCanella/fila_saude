#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "${1:-}" == "--demo" ]]; then
  exec python3 "${ROOT}/scripts/export_process_report.py" --demo
fi
exec python3 "${ROOT}/scripts/export_process_report.py" "$@"
