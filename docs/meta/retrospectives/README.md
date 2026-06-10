# Retrospectivas por fase

Registro curto de **processo e governança** ao concluir cada **FASE** (quando todos os cards da fase estão `done`).

## Quando rodar

1. Todos os cards com `phase: FASE-X` em `status: done` (ver `docs/planning/cards-backlog.md`).
2. Skill **phase-retrospective** — perguntas em um turno (~5 min).
3. Documentar **retro preenchida** ou **skip explícito** (soft gate: não bloqueia a fase seguinte).

## Arquivos

| Arquivo | Função |
|---------|--------|
| [`index.md`](index.md) | Índice: fase → status → arquivo → data |
| [`_template-fase-retro.md`](_template-fase-retro.md) | Modelo para copiar |
| `FASE-X-retro.md` | Uma retro por fase entregue |

Padrão de nome: **`FASE-X-retro.md`** (ex.: `FASE-1-retro.md`).

## Relação com outros artefatos

| Artefato | Foco |
|----------|------|
| **Retro por fase** | Processo, mocks, TDD, cards, regras, IA |
| [ADR](../../adr/) | Decisão técnica pontual |
| [delivery-log.md](../../delivery-log.md) | Entrega por CARD |
| [improving-the-template.md](../improving-the-template.md) | Sugestões para o repo **Modelo** (PR upstream) |

Itens estruturais para o template base: agregue nas retros e, quando fizer sentido, copie resumo para `improving-the-template.md`.

## FASE-0 (opcional)

Descoberta + bootstrap podem ser documentados em `FASE-0-retro.md` se o time quiser retro do setup inicial — não é obrigatório.

## Validação

```bash
./scripts/validate-phase-retros.sh
```

Emite **AVISO** se uma fase tem todos os cards `done` mas falta linha em `index.md` (`completed` ou `skipped`).
