#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STRICT="${QUALITY_SPEC_STRICT:-0}"
ARGS=()
[[ "$STRICT" == "1" ]] && ARGS+=(--strict)
exec python3 "${ROOT}/scripts/validate_quality_spec_plans.py" --root "$ROOT" "${ARGS[@]}"
