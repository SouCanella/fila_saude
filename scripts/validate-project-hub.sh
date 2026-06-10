#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HUB="${ROOT}/docs/meta/project-hub"
DATA="${HUB}/data"
ERR=0
fail() { echo "ERRO: $1"; ERR=1; }

for f in hub.data.json process.data.json quality.data.json security.data.json a11y.data.json design.data.json delivery.data.json learning.data.json journey.data.json tech_debt.data.json openapi.data.json release.data.json; do
  [[ -f "${DATA}/${f}" ]] || fail "ausente: ${f} — rode make hub-build"
done

python3 -c "
import json
h=json.load(open('${DATA}/hub.data.json'))
assert h.get('next_step', {}).get('prompt'), 'next_step.prompt vazio'
assert h.get('kpis') is not None, 'kpis ausente'
assert 'journey' in h, 'journey embutido no hub'
j=h.get('journey') or json.load(open('${DATA}/journey.data.json'))
assert j.get('data_mode') == 'showcase', 'template virgem: data_mode showcase'
assert j.get('report', {}).get('showcase_banner'), 'banner showcase esperado no template'
assert h.get('kpis', {}).get('openapi_valid') is False, 'template openapi stub'
entries = h.get('delivery', {}).get('entries') or []
assert not any(e.get('card_id') == 'CARD-XXX' for e in entries), 'placeholder CARD-XXX no delivery'
" || ERR=1

chmod +x "${ROOT}/scripts/check-hub-embeds.sh" 2>/dev/null || true
"${ROOT}/scripts/check-hub-embeds.sh" || ERR=1

python3 "${ROOT}/scripts/resolve_next_step.py" --root "$ROOT" --data-dir "$DATA" --json | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('prompt'), 'resolve_next_step sem prompt'
" || ERR=1

grep -q 'phaseFunnelSection' "${HUB}/hub-premium.js" || fail "hub-premium.js: phaseFunnelSection ausente"
grep -q 'renderSecurity' "${HUB}/hub-premium.js" || fail "hub-premium.js: renderSecurity ausente"
grep -q 'window.SecurityModule' "${HUB}/modules/security/security.js" || fail "security.js: export window ausente"

python3 "${ROOT}/scripts/test_build_project_journey.py" -q || ERR=1

if command -v node >/dev/null 2>&1; then
  node "${ROOT}/scripts/smoke-hub-modules.mjs" "$HUB" || ERR=1
else
  echo "AVISO: node ausente — smoke JS ignorado"
fi

[[ $ERR -eq 0 ]] && echo "OK: project hub"
exit $ERR
