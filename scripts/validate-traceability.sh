#!/usr/bin/env bash
# Valida alinhamento básico backlog ↔ traceability-matrix (avisos, não bloqueia CI do template vazio).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKLOG="${ROOT}/docs/backlog/mvp-backlog.md"
MATRIX="${ROOT}/docs/traceability-matrix.md"
WARN=0

warn() { echo "AVISO: $1"; WARN=1; }

if [[ ! -f "$BACKLOG" ]] || [[ ! -f "$MATRIX" ]]; then
  echo "AVISO: backlog ou matrix ausente — OK se descoberta ainda não iniciou"
  exit 0
fi

# REQ-NNN na tabela do backlog (linhas com | REQ- )
mapfile -t BACKLOG_REQS < <(grep -oE 'REQ-[0-9]+' "$BACKLOG" | sort -u || true)
mapfile -t MATRIX_REQS < <(grep -oE 'REQ-[0-9]+' "$MATRIX" | sort -u || true)

if [[ ${#BACKLOG_REQS[@]} -eq 0 ]] || [[ "${BACKLOG_REQS[0]:-}" == "" ]]; then
  echo "AVISO: nenhum REQ no backlog (pendente descoberta)"
  exit 0
fi

for req in "${BACKLOG_REQS[@]}"; do
  if ! grep -q "$req" "$MATRIX"; then
    warn "$req está no backlog mas não na traceability-matrix"
  fi
done

for req in "${MATRIX_REQS[@]}"; do
  [[ "$req" == "REQ_ID" ]] && continue
  if ! grep -q "$req" "$BACKLOG"; then
    warn "$req está na matrix mas não no backlog"
  fi
done

if [[ $WARN -eq 0 ]]; then
  echo "OK: backlog e matrix alinhados (${#BACKLOG_REQS[@]} REQ(s))"
else
  exit 0
fi
