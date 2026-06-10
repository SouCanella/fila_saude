#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCREENS="${ROOT}/design-references/screens"
SHARED="${ROOT}/design-references/shared"
ERR=0

echo "=== Validação protótipo HTML ==="

for required in design-tokens.css components.css mock-data.js mock-api.js mock-router.js; do
  if [[ ! -f "$SHARED/$required" ]]; then
    echo "FALTA shared/$required"
    ERR=1
  fi
done

if [[ ! -d "$SCREENS" ]]; then
  echo "FALTA design-references/screens/"
  exit 1
fi

shopt -s nullglob
for html in "$SCREENS"/*.html; do
  name=$(basename "$html")
  if ! grep -q 'components.css' "$html"; then
    echo "AVISO $name: não referencia components.css"
  fi
  for js in mock-data.js mock-api.js mock-router.js; do
    if grep -q "$js" "$html" && [[ ! -f "$SHARED/$js" ]]; then
      echo "FALTA $js referenciado em $name"
      ERR=1
    fi
  done
  echo "OK $name"
done

if [[ $ERR -eq 0 ]]; then
  echo "=== Protótipo HTML OK ==="
else
  exit 1
fi
