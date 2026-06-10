#!/usr/bin/env bash
# Repara cópia manual (cp -r) — aplica config de produto + marcador.
# Preferir: make create-project NAME="..." no Modelo upstream.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME=""
DRY=0

usage() {
  cat <<'EOF'
Uso: repair-product-config.sh --name "Nome do produto" [--dry-run]

Aplica template de produto em project.config.yaml e cria .modelo-product-workspace.
Use em pasta irmã criada manualmente (sem create-project).
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)
      [[ $# -ge 2 ]] || { echo "ERRO: --name exige valor" >&2; exit 1; }
      NAME="$2"
      shift 2
      ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERRO: opção desconhecida: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$NAME" ]]; then
  echo "ERRO: informe --name" >&2
  usage >&2
  exit 1
fi

if [[ -f "${ROOT}/.modelo-upstream" ]]; then
  echo "ERRO: esta pasta é Modelo upstream — use make create-project, não repair." >&2
  exit 2
fi

UPSTREAM_PATH=""
if [[ -f "${ROOT}/project.config.yaml" ]]; then
  UPSTREAM_PATH="$(python3 -c "
import re, sys
from pathlib import Path
t = Path(sys.argv[1]).read_text()
m = re.search(r'^  upstream_path:\s*\"?([^\"\\n]+)\"?', t, re.M)
print(m.group(1) if m else '')
" "${ROOT}/project.config.yaml" 2>/dev/null || true)"
fi

if [[ -z "$UPSTREAM_PATH" || ! -d "$UPSTREAM_PATH" ]]; then
  PARENT="$(dirname "$ROOT")"
  for candidate in "${PARENT}/Modelo" "${PARENT}/modelo"; do
    if [[ -f "${candidate}/.modelo-upstream" ]]; then
      UPSTREAM_PATH="$candidate"
      break
    fi
  done
fi

if [[ -z "$UPSTREAM_PATH" || ! -d "$UPSTREAM_PATH" ]]; then
  echo "ERRO: não foi possível localizar Modelo upstream (upstream_path ou ../Modelo)" >&2
  exit 1
fi

if [[ $DRY -eq 1 ]]; then
  echo "[dry-run] patch_product_config + write_product_marker em $ROOT"
  echo "[dry-run] upstream: $UPSTREAM_PATH"
  exit 0
fi

PRODUCT_NAME="$NAME" DEST_PATH="$ROOT" UPSTREAM_ROOT="$UPSTREAM_PATH" python3 <<'PY'
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.environ["UPSTREAM_ROOT"], "scripts"))
from modelo_spawn import patch_product_config, write_product_marker  # noqa: E402

patch_product_config(Path(os.environ["DEST_PATH"]), os.environ["PRODUCT_NAME"], Path(os.environ["UPSTREAM_ROOT"]))
write_product_marker(Path(os.environ["DEST_PATH"]))
print("OK: config de produto reparado")
PY

bash "${ROOT}/scripts/reset-hub-activity.sh" 2>/dev/null || true
echo "Próximo: make validate-spawn-context"
