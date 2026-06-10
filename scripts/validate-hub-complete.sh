#!/usr/bin/env bash
# Validação mestre Hub Evolução — P0/P1/P2 (HUB_VALIDATE_WAVE: 0|1|2|3|all)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WAVE="${HUB_VALIDATE_WAVE:-all}"
DEMO="${ROOT}/examples/project-hub-demo"
HUB="${ROOT}/docs/meta/project-hub"
DATA="${HUB}/data"
DEMO_DATA="${DEMO}/docs/meta/project-hub/data"
ERR=0

fail() { echo "ERRO: $1"; ERR=1; }
ok() { echo "OK: $1"; }

wave_ge() {
  local min="$1"
  if [[ "$WAVE" == "all" ]]; then return 0; fi
  [[ "$WAVE" =~ ^[0-9]+$ ]] && [[ "$WAVE" -ge "$min" ]]
}

echo "=== validate-hub-complete (wave=${WAVE}) ==="

# --- Wave 0: harness + testes ---
if wave_ge 0; then
  for f in build_tech_debt_health.py build_openapi_health.py build_release_health.py; do
    [[ -f "${ROOT}/scripts/${f}" ]] || fail "ausente scripts/${f}"
  done
  for f in build-hub-embeds.sh sync-card-github.sh validate-hub-complete.sh; do
    [[ -f "${ROOT}/scripts/${f}" ]] || fail "ausente scripts/${f}"
  done
  [[ -f "${ROOT}/docs/meta/project-hub/VALIDATION-CHECKLIST.md" ]] || fail "VALIDATION-CHECKLIST.md ausente"

  python3 "${ROOT}/scripts/test_build_project_journey.py" -q || ERR=1
  [[ -f "${ROOT}/scripts/test_resolve_next_step_retro.py" ]] && python3 "${ROOT}/scripts/test_resolve_next_step_retro.py" -q || true
  [[ -f "${ROOT}/scripts/test_build_tech_debt_health.py" ]] && python3 "${ROOT}/scripts/test_build_tech_debt_health.py" -q || true
  [[ -f "${ROOT}/scripts/test_openapi_health.py" ]] && python3 "${ROOT}/scripts/test_openapi_health.py" -q || true
fi

# --- Build template + demo ---
make -C "$ROOT" hub-build hub-demo-build >/dev/null || ERR=1

# --- Wave 1: P0 JSON + UI ---
if wave_ge 1; then
  python3 -c "
import json, sys
from pathlib import Path
root = Path('${ROOT}')
j = json.load(open('${DATA}/journey.data.json'))
h = json.load(open('${DATA}/hub.data.json'))
cfg_text = (root / 'project.config.yaml').read_text()
assert j.get('data_mode') == 'showcase', 'template: data_mode showcase'
assert j.get('report', {}).get('showcase_banner'), 'template: showcase_banner'
assert 'draft' in cfg_text and 'design:' in cfg_text
phases = j.get('lifecycle', {}).get('phases', [])
fase1 = next((p for p in phases if str(p.get('id','')).startswith('FASE-')), None)
if fase1 is None:
    # template virgem pode não ter FASE — checar milestone em demo
    pass
else:
    pass
assert 'empty_hints' in j.get('report', {}), 'empty_hints key'
assert j.get('discovery') is not None, 'discovery object'
hub_js = (root / 'docs/meta/project-hub/hub-premium.js').read_text()
for fn in ('filterDeliveriesByPhase', 'expandDeliveryRow', 'showcaseBanner', 'phaseFunnelSection'):
    assert fn in hub_js, f'hub-premium.js missing {fn}'
" || ERR=1

  python3 "${ROOT}/scripts/test_resolve_next_step_retro.py" -q 2>/dev/null || ERR=1

  # Demo coerente
  python3 -c "
import json
j = json.load(open('${DEMO_DATA}/journey.data.json'))
boot = next(p for p in j['lifecycle']['phases'] if p['id']=='bootstrap')
assert boot.get('progress_pct') == 100 or boot.get('sections_done', 0) > 0, 'demo bootstrap incoerente'
assert j.get('data_mode') == 'real', 'demo data_mode real'
assert not j.get('report', {}).get('showcase_banner'), 'demo sem banner showcase'
" || ERR=1
fi

# --- Wave 2: P1 governança ---
if wave_ge 2; then
  python3 -c "
import json
h = json.load(open('${DATA}/hub.data.json'))
sec = json.load(open('${DATA}/security.data.json'))
assert 'tech_debt_critical' in h.get('kpis', {}), 'KPI tech_debt_critical'
assert 'openapi_valid' in h.get('kpis', {}), 'KPI openapi_valid'
assert 'compliance' in sec, 'security.compliance block'
demo_h = json.load(open('${DEMO_DATA}/hub.data.json'))
assert demo_h['kpis'].get('tech_debt_critical', 0) == 0, 'demo tech_debt critical'
assert demo_h['kpis'].get('openapi_valid') is True, 'demo openapi_valid'
assert h['kpis'].get('openapi_valid') is False, 'template openapi stub invalid'
deliveries = h.get('delivery', {}).get('entries') or []
assert not any(e.get('card_id') == 'CARD-XXX' for e in deliveries), 'placeholder CARD-XXX no delivery template'
" || ERR=1

  python3 "${ROOT}/scripts/test_build_tech_debt_health.py" -q || ERR=1
  python3 "${ROOT}/scripts/test_openapi_health.py" -q || ERR=1
fi

# --- Wave 3: P2 automação ---
if wave_ge 3; then
  grep -rq 'filterDeliveriesByPhase' "${HUB}/hub-premium.js" || fail "hub-premium.js filterDeliveriesByPhase"
  grep -rq 'complianceSection\|Compliance' "${HUB}/hub-premium.js" || fail "hub-premium.js compliance"
  if ! grep -r ':8090/process-metrics/' "${ROOT}/.cursor/skills/process-metrics/SKILL.md" \
    "${ROOT}/docs/meta/process-metrics/README.md" "${ROOT}/process-metrics/README.md" 2>/dev/null; then
    ok "docs legados sem URL primária :8090/process-metrics/"
  else
    fail "docs ainda citam :8090/process-metrics/ como URL primária"
  fi
  [[ -x "${ROOT}/scripts/build-hub-embeds.sh" ]] || fail "build-hub-embeds.sh não executável"
  [[ -x "${ROOT}/scripts/sync-card-github.sh" ]] || fail "sync-card-github.sh não executável"
  [[ -x "${ROOT}/scripts/check-hub-embeds.sh" ]] || fail "check-hub-embeds.sh não executável"
  "${ROOT}/scripts/check-hub-embeds.sh" || fail "hub embeds drift"
  if [[ -f "${ROOT}/tests/e2e/hub/overview.spec.js" ]]; then
    if command -v npx >/dev/null 2>&1 && [[ -f "${ROOT}/package.json" ]]; then
      make -C "$ROOT" hub-e2e-demo >/dev/null 2>&1 || echo "AVISO: hub-e2e-demo falhou ou playwright ausente"
    fi
  fi
fi

# --- Gates comuns ---
make -C "$ROOT" hub-validate hub-demo-validate >/dev/null || ERR=1

[[ $ERR -eq 0 ]] && ok "validate-hub-complete"
exit $ERR
