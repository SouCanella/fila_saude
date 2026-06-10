# Ritual CI → Project Hub

O painel **Qualidade** e o **Overview** (`next_step`) refletem a última execução de testes apenas se o pipeline alimentar os JSON do hub após cada run.

## Sequência canônica (job CI)

1. **Testes** — unit, integração, contrato, E2E (conforme stack).
2. **`export-quality-run.sh`** — grava `quality-runs/latest.json` (e histórico) com JUnit + cobertura.
3. **`build-quality-health.sh`** — gera `quality-health.data.json` (legado).
4. **`build-project-hub.sh`** — regenera os 8 JSON em `docs/meta/project-hub/data/` (process, quality, security, a11y, design, delivery, learning, hub).

O template em `templates/ci/github-actions.yml.tpl` inclui os passos 2–4 com `if: always()` para que falhas de teste ainda atualizem o painel com gaps.

## Local (desenvolvedor)

```bash
./scripts/export-quality-run.sh --junit-unit-back reports/junit.xml --coverage-backend 85
make hub-build
make hub-serve   # :8090 → #quality
```

Alternativa manual: editar `quality-runs/manual.yaml` e rodar `make hub-build`.

## Refresh no browser

`POST /api/refresh` (botão **Atualizar** no hub) executa `build-project-hub.sh` — **não** roda testes. Para last-run real, exporte quality-run antes do refresh.

## Validação

```bash
make hub-validate
make hub-demo-build && make hub-demo-validate
```

O smoke `scripts/smoke-hub-modules.mjs` monta Security/A11y/Design com os JSON atuais.
