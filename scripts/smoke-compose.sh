#!/usr/bin/env bash
# Smoke test — serviços Docker healthy (REQ-001)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> postgres redis"
docker compose up -d postgres redis

echo "==> osrm (profile routing)"
docker compose --profile routing up -d osrm

echo "==> waiting for healthchecks..."
for i in $(seq 1 30); do
  unhealthy=$(docker compose ps --format json 2>/dev/null | python3 -c "
import json, sys
lines = [l for l in sys.stdin if l.strip()]
bad = []
for line in lines:
    try:
        o = json.loads(line)
    except json.JSONDecodeError:
        continue
    if o.get('Health') and o.get('Health') != 'healthy':
        bad.append(o.get('Service','?'))
if bad:
    print(','.join(bad))
" 2>/dev/null || true)
  if [[ -z "${unhealthy:-}" ]]; then
    docker compose ps
    echo "OK: compose services healthy"
    exit 0
  fi
  sleep 2
done

docker compose ps
echo "WARN: timeout waiting for all healthchecks — verify manually"
exit 1
