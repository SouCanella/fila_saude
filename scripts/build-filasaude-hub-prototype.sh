#!/usr/bin/env bash
# Gera ZIP do protótipo HTML FilaSaúde — Project Hub completo (offline-friendly)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEMO="${ROOT}/examples/project-hub-demo"
OUT="${ROOT}/exports/filasaude-hub-prototype"
ZIP="${ROOT}/exports/FilaSaude-Project-Hub-prototipo.zip"

echo "→ Build demo hub (dados base)…"
"${ROOT}/scripts/build-project-hub-demo.sh" >/dev/null

rm -rf "${OUT}"
mkdir -p "${OUT}/project-hub" "${OUT}/process-metrics" "${OUT}/quality-health" "${OUT}/design-references/screens" "${OUT}/design-references/shared"

# Hub core
HUB_SRC="${DEMO}/docs/meta/project-hub"
for f in index.html hub.js hub-data.js hub-premium.js legacy-templates.js premium.css premium-bridge.css guide.html; do
  cp "${HUB_SRC}/${f}" "${OUT}/project-hub/${f}"
done
cp -r "${HUB_SRC}/shared" "${HUB_SRC}/modules" "${HUB_SRC}/data" "${OUT}/project-hub/"

# Legacy embeds (Processo + Qualidade)
for f in index.html process-metrics.css process-metrics.js; do
  cp "${ROOT}/docs/meta/process-metrics/${f}" "${OUT}/process-metrics/" 2>/dev/null || true
done
for f in index.html quality-health.css quality-health.js; do
  cp "${ROOT}/docs/meta/quality-health/${f}" "${OUT}/quality-health/"
done
cp "${OUT}/project-hub/data/process.data.json" "${OUT}/process-metrics/process-metrics.data.json"
cp "${OUT}/project-hub/data/quality.data.json" "${OUT}/quality-health/quality-health.data.json"

# Design mocks FilaSaúde (gerados pelo script Python)
python3 "${ROOT}/scripts/customize-filasaude-prototype.py" \
  --hub-data "${OUT}/project-hub/data" \
  --design-dir "${OUT}/design-references" \
  --hub-html "${OUT}/project-hub/index.html"

# Offline: embute JSON para abrir sem servidor (file://)
python3 "${ROOT}/scripts/embed-hub-prototype-data.py" "${OUT}"

# README + serve helper
cp "${ROOT}/exports/filasaude-hub-prototype.README.md" "${OUT}/README.md" 2>/dev/null || true

cat > "${OUT}/serve.sh" <<'EOF'
#!/usr/bin/env bash
cd "$(dirname "$0")"
echo "FilaSaúde Project Hub → http://localhost:8080/project-hub/"
python3 -m http.server 8080
EOF
chmod +x "${OUT}/serve.sh"

cat > "${OUT}/index.html" <<'EOF'
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta http-equiv="refresh" content="0; url=project-hub/index.html" />
  <title>FilaSaúde — Project Hub</title>
</head>
<body>
  <p><a href="project-hub/index.html">Abrir Project Hub FilaSaúde</a></p>
</body>
</html>
EOF

mkdir -p "${ROOT}/exports"
rm -f "${ZIP}"
(cd "${ROOT}/exports" && zip -rq "$(basename "${ZIP}")" filasaude-hub-prototype)

echo "OK: ${ZIP}"
echo "    Descompacte e abra index.html ou rode ./serve.sh"
