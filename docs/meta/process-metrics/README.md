# Painel de métricas do processo (método Modelo)

Ferramenta de **governança do template** — não faz parte do protótipo visual do produto (`design-references/`).

## Fonte da verdade

- `../process-timeline.yaml`
- `../process-metrics.md`

## Gerar dados e abrir

```bash
make hub-build
make hub-serve
# Processo: http://localhost:8090/project-hub/#process
# Overview (funil + entregas): http://localhost:8090/project-hub/#overview
```

Legado standalone:

```bash
./scripts/build-process-metrics.sh
./scripts/serve-process-metrics.sh
```

O servidor sobe em `docs/meta/` (não só na pasta do painel) para o link **Guia de métricas** funcionar — `../process-metrics.md` dava 404 no `http.server` da subpasta.

## Previsões no relatório

Datas e barras **roxas / (est.)** são **projeção estatística** (médias históricas + encadeamento). **Não** são datas de negócio, SLA ou compromisso com cliente.

## Cards no Gantt

Prioridade: `opened_at` / `done_at` em `docs/tracking/cards/CARD-XXX.md` → fallback nas rodadas do timeline.
