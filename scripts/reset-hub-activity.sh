#!/usr/bin/env bash
# Zera horas (métricas de processo) e fontes de atividade recente no Project Hub.
# Use após copiar o template Modelo para um produto novo — sozinho ou via make init-new-project.
#
# Limpa:
#   - docs/meta/process-timeline.yaml (rounds, sessions, milestones)
#   - docs/meta/process-metrics-log.md
#   - docs/meta/quality-runs/manual.yaml e latest.json
#   - process_metrics.project_started_at e active_context em project.config.yaml
#   - JSON do hub (rebuild)
#
# Atividade no Overview: rodadas/entregas/cards ativos habilitam o feed de artefatos
# (project-artifacts.yaml). Projeto virgem sem métricas → feed vazio após rebuild.
# git init limpo evita datas antigas quando o feed for habilitado.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TPL="${ROOT}/templates/new-project"
DRY=0
REBUILD=1

usage() {
  cat <<'EOF'
Uso: scripts/reset-hub-activity.sh [opções]

  --dry-run     Mostra o que seria alterado, sem gravar
  --no-rebuild  Não roda build-project-hub / process-metrics / quality-health
  --root PATH   Raiz do projeto (default: pasta do script/..)
  -h, --help    Esta ajuda

Atalho: make reset-hub-activity
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY=1; shift ;;
    --no-rebuild) REBUILD=0; shift ;;
    --root)
      [[ $# -ge 2 ]] || { echo "ERRO: --root exige caminho" >&2; exit 1; }
      ROOT="$(cd "$2" && pwd)"
      TPL="${ROOT}/templates/new-project"
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERRO: opção desconhecida: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ ! -d "$TPL" ]]; then
  echo "ERRO: templates/new-project ausente em $ROOT" >&2
  exit 1
fi

run() {
  if [[ $DRY -eq 1 ]]; then
    echo "[dry-run] $*"
  else
    "$@"
  fi
}

copy_tpl() {
  local name="$1"
  local dest="$2"
  local src="${TPL}/${name}"
  if [[ ! -f "$src" ]]; then
    echo "ERRO: template ausente: $src" >&2
    exit 1
  fi
  if [[ $DRY -eq 1 ]]; then
    echo "[dry-run] cp $src -> $dest"
  else
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    echo "OK: $dest"
  fi
}

reset_config_metrics() {
  local cfg="${ROOT}/project.config.yaml"
  if [[ ! -f "$cfg" ]]; then
    echo "AVISO: project.config.yaml ausente — pulando reset de process_metrics"
    return 0
  fi
  if [[ $DRY -eq 1 ]]; then
    echo "[dry-run] reset process_metrics.project_started_at e active_context em $cfg"
    return 0
  fi
  python3 - "$cfg" <<'PY'
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
orig = text

def repl_field(field: str, body: str, value: str = "null") -> str:
    pattern = rf"(^  {re.escape(field)}:).*$"
    return re.sub(pattern, rf"\1 {value}", body, count=1, flags=re.MULTILINE)

text = repl_field("project_started_at", text)
text = repl_field("active_context", text)

if text == orig:
    print(f"OK: process_metrics já virgem em {path.name}")
else:
    path.write_text(text, encoding="utf-8")
    print(f"OK: process_metrics zerado em {path.name}")
PY
}

echo "=== reset-hub-activity ==="
echo "Raiz: $ROOT"

if [[ -d "${ROOT}/.git" ]]; then
  echo ""
  echo "AVISO: .git presente — o feed de atividade no hub ainda pode listar commits antigos."
  echo "  Para projeto novo: rm -rf .git && git init"
  echo ""
fi

copy_tpl process-timeline.yaml "${ROOT}/docs/meta/process-timeline.yaml"
copy_tpl process-metrics-log.md "${ROOT}/docs/meta/process-metrics-log.md"
copy_tpl quality-runs-manual.yaml "${ROOT}/docs/meta/quality-runs/manual.yaml"

if [[ -f "${ROOT}/docs/meta/quality-runs/latest.json" ]]; then
  run rm -f "${ROOT}/docs/meta/quality-runs/latest.json"
  echo "OK: removido docs/meta/quality-runs/latest.json"
fi

reset_config_metrics

if [[ $REBUILD -eq 1 && $DRY -eq 0 ]]; then
  bash "${ROOT}/scripts/build-project-hub.sh"
  bash "${ROOT}/scripts/build-process-metrics.sh"
  bash "${ROOT}/scripts/build-quality-health.sh"
  echo ""
  echo "=== Hub reconstruído — horas e atividade de métricas zeradas ==="
  echo "Verifique: make hub-serve → #overview (esforço 0h) e #process"
elif [[ $REBUILD -eq 1 && $DRY -eq 1 ]]; then
  echo "[dry-run] build-project-hub.sh + build-process-metrics.sh + build-quality-health.sh"
fi

if [[ $DRY -eq 1 ]]; then
  echo ""
  echo "=== dry-run concluído (nenhum arquivo alterado) ==="
fi
