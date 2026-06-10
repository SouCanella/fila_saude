#!/usr/bin/env bash
# Valida alinhamento Fase → Card → REQ (avisos; falha só em inconsistências graves pós-planejamento MVP).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKLOG="${ROOT}/docs/backlog/mvp-backlog.md"
CARDS_INDEX="${ROOT}/docs/planning/cards-backlog.md"
PHASES="${ROOT}/docs/planning/mvp-phases.md"
CARDS_DIR="${ROOT}/docs/tracking/cards"
MATRIX="${ROOT}/docs/traceability-matrix.md"
CONFIG="${ROOT}/project.config.yaml"
WARN=0
ERR=0

warn() { echo "AVISO: $1"; WARN=1; }
fail() { echo "ERRO: $1"; ERR=1; }

MVP_STATUS=$(grep -A5 "^mvp_planning:" "$CONFIG" 2>/dev/null | grep "status:" | head -1 | awk '{print $2}' || echo "pending")

if [[ ! -f "$BACKLOG" ]] || [[ ! -f "$CARDS_INDEX" ]]; then
  echo "AVISO: backlog ou cards-backlog ausente — OK antes do planejamento MVP"
  exit 0
fi

if [[ -d "$CARDS_DIR" ]]; then
  for card_file in "$CARDS_DIR"/CARD-*.md; do
    [[ -f "$card_file" ]] || continue
    base=$(basename "$card_file")
    [[ "$base" == _template* ]] && continue
    cid=$(grep -E '^id:' "$card_file" 2>/dev/null | head -1 | sed 's/^id: *//' || echo "${base%.md}")
    if ! grep -qF "$cid" "$CARDS_INDEX" 2>/dev/null; then
      fail "$cid em docs/tracking/cards/ sem linha em cards-backlog.md"
    fi
  done
fi

mapfile -t BACKLOG_REQS < <(grep -oE 'REQ-[A-Za-z0-9-]+' "$BACKLOG" | sort -u || true)
mapfile -t CARD_IDS < <(grep -oE 'CARD-[A-Za-z0-9]+(-[A-Za-z0-9]+)*' "$CARDS_INDEX" | sort -u || true)

if [[ ${#BACKLOG_REQS[@]} -eq 0 ]] || [[ "${BACKLOG_REQS[0]:-}" == "" ]]; then
  if [[ $ERR -eq 1 ]]; then
    exit 1
  fi
  echo "AVISO: nenhum REQ no mvp-backlog (pendente planejamento MVP)"
  exit 0
fi

for req in "${BACKLOG_REQS[@]}"; do
  [[ "$req" == "REQ_ID" ]] && continue
  if ! grep -q "$req" "$CARDS_INDEX" 2>/dev/null; then
    if [[ "$MVP_STATUS" == "complete" ]]; then
      fail "$req no backlog sem referência em cards-backlog.md"
    else
      warn "$req no backlog sem card ainda (completar planejamento MVP)"
    fi
  fi
done

for card in "${CARD_IDS[@]}"; do
  [[ "$card" == "CARD_ID" ]] && continue
  if ! find "$CARDS_DIR" -name "${card}*.md" ! -name "_template*" 2>/dev/null | grep -q .; then
    if [[ "$MVP_STATUS" == "complete" ]]; then
      fail "$card listado em cards-backlog sem arquivo em docs/tracking/cards/"
    else
      warn "$card sem arquivo MD ainda"
    fi
  fi
done

if [[ -f "$PHASES" ]]; then
  for card in "${CARD_IDS[@]}"; do
    [[ "$card" == "CARD_ID" ]] && continue
    phase_line=$(grep "$card" "$CARDS_INDEX" || true)
    if [[ -n "$phase_line" ]]; then
      phase=$(echo "$phase_line" | grep -oE 'FASE-[0-9]+' | head -1 || true)
      if [[ -n "$phase" ]] && ! grep -q "$phase" "$PHASES"; then
        warn "$card referencia $phase ausente em mvp-phases.md"
      fi
    fi
  done
fi

if [[ -f "$MATRIX" ]]; then
  for req in "${BACKLOG_REQS[@]}"; do
    [[ "$req" == "REQ_ID" ]] && continue
    if ! grep -q "$req" "$MATRIX"; then
      warn "$req no backlog sem linha na traceability-matrix"
    fi
  done
fi

if [[ $ERR -eq 1 ]]; then
  exit 1
fi

if [[ $WARN -eq 0 ]]; then
  echo "OK: planejamento alinhado (${#BACKLOG_REQS[@]} REQ(s), ${#CARD_IDS[@]} CARD(s) no índice)"
fi

if [[ -x "${ROOT}/scripts/validate-phase-retros.sh" ]]; then
  "${ROOT}/scripts/validate-phase-retros.sh" || true
fi

exit 0
