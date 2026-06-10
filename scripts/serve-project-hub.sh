#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${HUB_PORT:-${1:-8090}}"
BUILD="${ROOT}/scripts/build-project-hub.sh"

"${BUILD}"
chmod +x "${ROOT}/scripts/hub-serve-symlinks.sh"
"${ROOT}/scripts/hub-serve-symlinks.sh" "$ROOT"
exec python3 "${ROOT}/scripts/project_hub_server.py" \
  --repo-root "$ROOT" \
  --serve-dir "$ROOT" \
  --port "$PORT" \
  --build-script "$BUILD"
