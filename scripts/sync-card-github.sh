#!/usr/bin/env bash
# Sync CARD MD ↔ GitHub Issues (requer gh auth).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DRY_RUN=0

usage() {
  echo "Uso: sync-card-github.sh {open|close|comment} CARD-XXX [--dry-run] [--body TEXT]"
  exit 1
}

[[ $# -ge 2 ]] || usage
ACTION="$1"
CARD_ID="$2"
shift 2
BODY=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --body) BODY="$2"; shift ;;
    *) echo "Arg desconhecido: $1"; usage ;;
  esac
  shift
done

CARDS_DIR="${ROOT}/docs/tracking/cards"
[[ -f "${CARDS_DIR}/${CARD_ID}.md" ]] || CARDS_DIR="${ROOT}/tracking/cards"
CARD_PATH="${CARDS_DIR}/${CARD_ID}.md"
[[ -f "$CARD_PATH" ]] || { echo "ERRO: ${CARD_PATH} ausente"; exit 1; }

TITLE=$(grep -E '^title:' "$CARD_PATH" | head -1 | sed 's/^title: *//')
TITLE="${TITLE:-$CARD_ID}"

run_gh() {
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "[dry-run] gh $*"
    return 0
  fi
  if ! command -v gh >/dev/null 2>&1; then
    echo "ERRO: gh não encontrado — instale GitHub CLI e autentique (gh auth login)" >&2
    exit 1
  fi
  gh "$@"
}

case "$ACTION" in
  open)
    if [[ $DRY_RUN -eq 1 ]]; then
      echo "[dry-run] gh issue create --title \"${CARD_ID}: ${TITLE}\""
      python3 "${ROOT}/scripts/update_card_frontmatter.py" "$CARD_PATH" \
        --dry-run --set "external_url=https://github.com/example/repo/issues/0"
      URL=""
    else
      URL=$(run_gh issue create --title "${CARD_ID}: ${TITLE}" --body "Card ${CARD_ID} — sync automático Modelo")
      echo "Issue: $URL"
      if [[ -n "$URL" ]]; then
        python3 "${ROOT}/scripts/update_card_frontmatter.py" "$CARD_PATH" \
          --set "external_url=${URL}"
      fi
    fi
    ;;
  close)
    NUM=$(grep -E '^external_url:' "$CARD_PATH" | grep -oE '[0-9]+$' || true)
    [[ -n "$NUM" ]] || { echo "ERRO: external_url ausente em ${CARD_PATH}"; exit 1; }
    run_gh issue close "$NUM"
    ;;
  comment)
    NUM=$(grep -E '^external_url:' "$CARD_PATH" | grep -oE '[0-9]+$' || true)
    [[ -n "$NUM" ]] || { echo "ERRO: external_url ausente"; exit 1; }
    run_gh issue comment "$NUM" --body "${BODY:-Atualização via sync-card-github.sh}"
    ;;
  *) usage ;;
esac

echo "OK: sync-card-github ${ACTION} ${CARD_ID}"
