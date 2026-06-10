# Benchmarks de processo (método Modelo)

Agregação **anonimizada** de métricas de projetos que usaram o template — base de conhecimento para estimar o próximo projeto.

**Não inclui:** nome do produto, domínio, dados de usuário, conteúdo de specs.

## Contribuir

Após planejamento MVP ou ao encerrar o projeto:

```bash
./scripts/build-process-metrics.sh
./scripts/export-process-benchmark.sh
./scripts/aggregate-process-benchmarks.sh   # atualiza index.md com medianas
```

Isso gera `snapshots/benchmark-YYYY-MM-DDTHH-MM.json` nesta pasta (versionável no repo Modelo ou cópia manual).

Skill da IA: **process-benchmark** (export + pergunta retro: previsão MVP (est.) vs data real do último card).

## Campos típicos do snapshot

| Campo | Uso |
|-------|-----|
| `stack` | backend/frontend abstratos |
| `phase_count`, `card_count` | Escala do MVP |
| `calendar_ratio` | Razão calendário/esforço observada |
| `activity_averages` | Médias por atividade (rodadas) |
| `forecasts_disclaimer` | Lembrete: projeções ≠ negócio |

## Uso em novo projeto

Compare ranges dos snapshots com o painel do projeto atual (`docs/meta/process-metrics/`). Previsões continuam **estatísticas** — não substituem planejamento comercial.

Ver também [improving-the-template.md](../improving-the-template.md) e retros em [retrospectives/](../retrospectives/).
