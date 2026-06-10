---
name: process-benchmark
description: Export anonymized process metrics snapshot and refresh benchmarks index. Use when mvp_planning completes, MVP ends, or phase retrospective asks for cross-project learning.
---

# Process benchmark

## When

- `mvp_planning.status: complete` (baseline opcional)
- Fim de fase / fim do MVP (retro)
- Humano pede contribuir para base de conhecimento do método

## Steps

1. `./scripts/build-process-metrics.sh` (ou demo: `build-process-metrics-demo.sh`)
2. `./scripts/export-process-benchmark.sh`
3. `./scripts/aggregate-process-benchmarks.sh` — atualiza `docs/meta/process-benchmarks/index.md`

## Retro (pergunta fixa)

Na retrospectiva de fase, registre:

- **Previsão MVP (est.)** no início da fase (painel → aba Previsões)
- **Data real** do último card `done_at` da fase
- Diferença em dias (calendário) — aprendizado, não SLA

## Não exportar

Nome do produto, domínio, conteúdo de specs, PII.
