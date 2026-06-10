#!/usr/bin/env bash
# Valida se o workspace é upstream Modelo vs produto spawnado.
# STRICT=1 → exit 1 em violações (upstream com artefatos de produto sem dev mode).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STRICT="${STRICT:-0}"
ERR=0

warn() { echo "AVISO spawn: $1"; }
fail() { echo "ERRO spawn: $1"; ERR=1; }

if [[ ! -f "${ROOT}/project.config.yaml" ]]; then
  fail "project.config.yaml ausente"
  exit 1
fi

eval "$(python3 - "${ROOT}/project.config.yaml" <<'PY'
import re
import shlex
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

def yaml_val(key: str, section: str | None = None) -> str | None:
    if section:
        m = re.search(rf"^{re.escape(section)}:\s*\n(?:  .+\n)*?  {re.escape(key)}:\s*(.+)$", text, re.M)
    else:
        m = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, re.M)
    if not m:
        return None
    return m.group(1).strip().strip('"').strip("'")

is_upstream = yaml_val("is_upstream", "template") == "true"
dev_mode = yaml_val("upstream_dev_mode", "template") == "true"
spawn_required = yaml_val("sibling_spawn_required", "template") == "true"
is_product = (Path(sys.argv[1]).parent / ".modelo-product-workspace").is_file()
disc = yaml_val("status", "discovery") or "pending"
boot = yaml_val("status", "bootstrap") or "incomplete"
pname = yaml_val("name", "project")
spawned = yaml_val("is_upstream", "template") == "false" or is_product

print(f"IS_UPSTREAM={int(is_upstream)}")
print(f"DEV_MODE={int(dev_mode)}")
print(f"SPAWN_REQUIRED={int(spawn_required)}")
print(f"IS_PRODUCT_MARKER={int(is_product)}")
print(f"DISCOVERY_STATUS={disc}")
print(f"BOOTSTRAP_STATUS={boot}")
print(f"PROJECT_NAME={shlex.quote(pname or '')}")
print(f"SPAWNED_PRODUCT={int(spawned and not is_upstream)}")
PY
)"

echo "=== validate-spawn-context ==="
echo "Raiz: $ROOT"

if [[ "$SPAWNED_PRODUCT" -eq 1 ]] || [[ "$IS_UPSTREAM" -eq 0 ]]; then
  echo "Contexto: workspace de produto (spawn) — discovery/bootstrap/mocks nesta pasta."
  if [[ -f "${ROOT}/.modelo-upstream" ]]; then
    fail "produto spawnado não deve ter .modelo-upstream (remova ou recrie via create-project)"
  fi
  if [[ "$DEV_MODE" -eq 1 ]]; then
    fail "produto não deve ter upstream_dev_mode: true — make repair-product-config NAME=\"...\" ou recrie via create-project"
  fi
  if [[ "$IS_UPSTREAM" -eq 1 ]]; then
    fail "produto deve ter template.is_upstream: false"
  fi
  if [[ -d "${ROOT}/.github" ]]; then
    fail "produto não deve copiar .github/ do upstream — CI nasce no bootstrap (templates/ci/)"
  fi
  if [[ -f "${ROOT}/EVOLUCAO-MODELO.md" ]]; then
    fail "produto não deve incluir EVOLUCAO-MODELO.md (roadmap do template upstream)"
  fi
  if [[ -d "${ROOT}/examples" ]]; then
    fail "produto não deve copiar examples/ do upstream"
  fi
  if [[ -f "${ROOT}/docs/meta/improving-the-template.md" ]]; then
    fail "produto não deve incluir docs/meta/improving-the-template.md (meta upstream)"
  fi
  for demo in "${ROOT}"/scripts/*demo*; do
    [[ -e "$demo" ]] || continue
    fail "produto não deve copiar scripts demo do upstream: $(basename "$demo")"
  done
  if [[ $ERR -eq 0 ]]; then
    echo "OK: config de produto válida."
  fi
  if [[ "$STRICT" == "1" && $ERR -ne 0 ]]; then
    exit 1
  fi
  exit "$ERR"
fi

if [[ "$IS_UPSTREAM" -eq 1 ]] && [[ "$DEV_MODE" -eq 1 ]]; then
  echo "OK: Modelo upstream em upstream_dev_mode (evolução do template)."
  if [[ "$DISCOVERY_STATUS" != "pending" ]] || [[ -n "$PROJECT_NAME" && "$PROJECT_NAME" != "null" ]]; then
    warn "há sinais de produto no upstream — confirme que é evolução intencional do template"
  fi
  exit 0
fi

# Upstream sem dev mode — não deve ter trabalho de produto
echo "Contexto: Modelo upstream — produto novo deve usar make create-project (pasta irmã)."

if [[ "$DISCOVERY_STATUS" != "pending" ]]; then
  fail "discovery.status=$DISCOVERY_STATUS no upstream — rode make create-project e trabalhe na pasta irmã"
fi

if [[ -n "$PROJECT_NAME" && "$PROJECT_NAME" != "null" ]]; then
  fail "project.name preenchido no upstream — spawn obrigatório antes de discovery"
fi

if [[ "$BOOTSTRAP_STATUS" == "complete" ]]; then
  fail "bootstrap completo no upstream sem upstream_dev_mode — use pasta irmã"
fi

# Telas além do set template no upstream sem dev mode
SCREENS_DIR="${ROOT}/design-references/screens"
ALLOWED_SCREENS="login.html dashboard.html item-form.html _template-screen.html"
if [[ -d "$SCREENS_DIR" ]]; then
  for screen in "$SCREENS_DIR"/*.html; do
    [[ -e "$screen" ]] || continue
    base="$(basename "$screen")"
    if ! echo " $ALLOWED_SCREENS " | grep -q " ${base} "; then
      fail "tela extra em design-references/screens/ no upstream: $base — use pasta irmã ou upstream_dev_mode"
    fi
  done
fi

# Heurística: discovery preenchida com produto real
if [[ -f "${ROOT}/docs/discovery/product-discovery.md" ]]; then
  if grep -qE '^\*\*Produto:\*\*|^## Visão' "${ROOT}/docs/discovery/product-discovery.md" 2>/dev/null; then
    if grep -qv '^\[Preencher\]|^_\.\.\._|placeholder' "${ROOT}/docs/discovery/product-discovery.md" 2>/dev/null; then
      body_lines=$(grep -cE '.+' "${ROOT}/docs/discovery/product-discovery.md" || true)
      if [[ "$body_lines" -gt 8 ]]; then
        fail "docs/discovery/product-discovery.md parece preenchido no upstream — use pasta irmã"
      fi
    fi
  fi
fi

if [[ $ERR -eq 0 ]]; then
  echo "OK: upstream sem sinais de produto ativo (use create-project para novo app)."
else
  echo ""
  echo "Correção: cd Modelo && make create-project NAME=\"<produto>\" GIT_INIT=1"
  echo "Depois: abrir a pasta irmã no Cursor. Ver docs/operations/spawn-project.md"
fi

if [[ "$STRICT" == "1" && $ERR -ne 0 ]]; then
  exit 1
fi
exit 0
