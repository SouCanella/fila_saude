#!/usr/bin/env bash
# Deprecated — use serve-project-hub.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${1:-8090}"
exec "${ROOT}/scripts/serve-project-hub.sh" "$PORT"
