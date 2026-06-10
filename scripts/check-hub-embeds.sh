#!/usr/bin/env bash
# Verifica que embeds do hub batem com build-hub-embeds.sh (anti-drift).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HUB="${ROOT}/docs/meta/project-hub"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

"${ROOT}/scripts/build-hub-embeds.sh" "${TMP}/hub"
ERR=0
for pair in "process/process.js" "quality/quality.js"; do
  mod="${pair%%/*}"
  file="${pair##*/}"
  expected="${TMP}/hub/modules/${mod}/${file}"
  committed="${HUB}/modules/${mod}/${file}"
  if [[ ! -f "$committed" ]]; then
    echo "ERRO: ausente ${committed}" >&2
    ERR=1
    continue
  fi
  if ! diff -q "$expected" "$committed" >/dev/null 2>&1; then
    echo "ERRO: drift em modules/${mod}/${file} — rode make hub-build" >&2
    ERR=1
  fi
done
[[ $ERR -eq 0 ]] && echo "OK: hub embeds alinhados"
exit $ERR
