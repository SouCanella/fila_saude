#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JSON="${ROOT}/docs/meta/quality-health/quality-health.data.json"

if [[ ! -f "$JSON" ]]; then
  echo "AVISO: quality-health.data.json ausente — rode make quality-build"
  exit 0
fi

python3 -c "
import json, sys
from pathlib import Path
data = json.loads(Path('$JSON').read_text())
gaps = data.get('gaps') or []
if gaps:
    print(f'AVISO: {len(gaps)} REQ(s) com gaps de teste (aba Gaps no painel)')
else:
    print('OK: saúde da qualidade')
"
