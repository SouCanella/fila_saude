#!/usr/bin/env bash
# Zera artefatos de entrega do repo Modelo upstream — use após copiar o template para um produto novo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TPL="${ROOT}/templates/new-project"
DRY=0
[[ "${1:-}" == "--dry-run" ]] && DRY=1

if [[ ! -d "$TPL" ]]; then
  echo "ERRO: templates/new-project ausente" >&2
  exit 1
fi

run() {
  if [[ $DRY -eq 1 ]]; then
    echo "[dry-run] $*"
  else
    "$@"
  fi
}

echo "=== init-new-project ==="
echo "Raiz: $ROOT"

if [[ -f "${ROOT}/.modelo-product-workspace" && $DRY -eq 0 ]]; then
  python3 "${ROOT}/scripts/modelo_spawn.py" --prune "$ROOT" || true
fi

if [[ ! -f "${ROOT}/.modelo-upstream" && ! -f "${ROOT}/.modelo-product-workspace" ]]; then
  echo "ERRO: workspace sem marcador upstream nem produto." >&2
  echo "  Produto novo: make create-project NAME=\"...\" no Modelo upstream (pasta irmã)." >&2
  echo "  Cópia manual legada: make repair-product-config NAME=\"...\"" >&2
  echo "  Ver docs/operations/spawn-project.md" >&2
  exit 2
fi

if [[ -d "${ROOT}/.git" ]]; then
  echo ""
  echo "AVISO: pasta .git detectada. Atividade recente no hub usa histórico git."
  echo "  Para projeto novo do zero, considere:"
  echo "    rm -rf .git && git init"
  echo ""
fi

copy_tpl() {
  local name="$1"
  local dest="$2"
  if [[ $DRY -eq 1 ]]; then
    echo "[dry-run] cp $TPL/$name -> $dest"
  else
    cp "$TPL/$name" "$dest"
    echo "OK: $dest"
  fi
}

copy_tpl delivery-log.md "${ROOT}/docs/delivery-log.md"
copy_tpl traceability-matrix.md "${ROOT}/docs/traceability-matrix.md"
copy_tpl cards-backlog.md "${ROOT}/docs/planning/cards-backlog.md"

for f in "${ROOT}"/docs/tracking/cards/CARD-Hub-*.md; do
  [[ -e "$f" ]] || continue
  run rm -f "$f"
  echo "OK: removido $(basename "$f")"
done

for f in "${ROOT}"/docs/specs/REQ-Hub-*.md; do
  [[ -e "$f" ]] || continue
  run rm -f "$f"
  echo "OK: removido $(basename "$f")"
done

if [[ $DRY -eq 0 ]]; then
  chmod +x "${ROOT}/scripts"/*.sh 2>/dev/null || true
  bash "${ROOT}/scripts/reset-hub-activity.sh"
  echo ""
  echo "=== Projeto pronto para descoberta/bootstrap ==="
  echo "Próximo: docs/00-getting-started.md · make hub-serve"
else
  bash "${ROOT}/scripts/reset-hub-activity.sh" --dry-run
  echo ""
  echo "=== dry-run concluído (nenhum arquivo alterado) ==="
fi
