#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="${1:-${ROOT}/project.config.yaml}"
DATA="${ROOT}/docs/meta/project-hub/data/openapi.data.json"

python3 "${ROOT}/scripts/build_openapi_health.py" --root "$ROOT" --config "$CONFIG" --json "$DATA"

python3 -c "
import json, sys
d=json.load(open('$DATA'))
assert d.get('report', {}).get('parseable'), 'openapi não parseável'
print('OK: openapi validado')
"
