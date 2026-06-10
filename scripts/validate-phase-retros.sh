#!/usr/bin/env bash
# Avisa se uma FASE tem todos os cards done mas falta retro/skip em meta/retrospectives/index.md
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CARDS_INDEX="${ROOT}/docs/planning/cards-backlog.md"
RETRO_INDEX="${ROOT}/docs/meta/retrospectives/index.md"
CARDS_DIR="${ROOT}/docs/tracking/cards"
WARN=0

warn() { echo "AVISO: $1"; WARN=1; }

card_status() {
  local card="$1"
  local f
  f=$(find "$CARDS_DIR" -maxdepth 1 -name "${card}*.md" ! -name "_template*" 2>/dev/null | head -1 || true)
  if [[ -n "$f" ]]; then
    grep -E '^status:' "$f" 2>/dev/null | head -1 | awk '{print $2}' || echo "open"
  else
    echo "open"
  fi
}

retro_documented() {
  local phase="$1"
  [[ -f "${ROOT}/docs/meta/retrospectives/${phase}-retro.md" ]] && return 0
  awk -F'|' -v p="$phase" '
    NF >= 3 {
      gsub(/^[ \t]+|[ \t]+$/, "", $2)
      gsub(/^[ \t]+|[ \t]+$/, "", $3)
      if ($2 == p && ($3 == "completed" || $3 == "skipped")) { found=1 }
    }
    END { exit !found }
  ' "$RETRO_INDEX" 2>/dev/null
}

if [[ ! -f "$CARDS_INDEX" ]]; then
  echo "AVISO: cards-backlog ausente — OK antes da descoberta"
  exit 0
fi

if [[ ! -f "$RETRO_INDEX" ]]; then
  warn "docs/meta/retrospectives/index.md ausente"
  exit 0
fi

declare -A SEEN_PHASE=()

while IFS= read -r line; do
  [[ "$line" != \|*CARD-* ]] && continue
  card=$(echo "$line" | awk -F'|' '{gsub(/ /,"",$2); print $2}')
  phase=$(echo "$line" | awk -F'|' '{gsub(/ /,"",$3); print $3}')
  [[ "$card" != CARD-* ]] && continue
  [[ "$phase" != FASE-* ]] && continue
  SEEN_PHASE["$phase"]=1
done < "$CARDS_INDEX"

for phase in "${!SEEN_PHASE[@]}"; do
  cards=()
  while IFS= read -r line; do
    [[ "$line" != \|*CARD-* ]] && continue
    p=$(echo "$line" | awk -F'|' '{gsub(/ /,"",$3); print $3}')
    [[ "$p" != "$phase" ]] && continue
    c=$(echo "$line" | awk -F'|' '{gsub(/ /,"",$2); print $2}')
    [[ "$c" == CARD-* ]] && cards+=("$c")
  done < "$CARDS_INDEX"

  [[ ${#cards[@]} -eq 0 ]] && continue

  all_done=1
  for c in "${cards[@]}"; do
    st=$(card_status "$c")
    if [[ "$st" != "done" ]]; then
      all_done=0
      break
    fi
  done

  [[ "$all_done" -eq 0 ]] && continue

  if ! retro_documented "$phase"; then
    warn "${phase}: todos os cards done — falta retro (completed) ou skip em docs/meta/retrospectives/"
  fi
done

if [[ $WARN -eq 0 ]]; then
  echo "OK: retrospectivas de fase (nenhuma fase completa pendente de documentação)"
else
  [[ "${RETRO_STRICT:-0}" == "1" ]] && exit 1
fi
exit 0
