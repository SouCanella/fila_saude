# Fatiamento — Fase → Card → REQ

Como organizar o produto antes de specs e código.

## Hierarquia

| Nível | ID | Onde | Papel |
|-------|-----|------|--------|
| **Fase** | `FASE-1`… | [mvp-phases.md](../planning/mvp-phases.md) | Marco do plano (MVP, v1.1…) |
| **Card** | `CARD-001`… | [cards-backlog.md](../planning/cards-backlog.md) + [tracking/cards/](../tracking/cards/) | **Unidade de trabalho** — abrir, desenvolver, fechar |
| **REQ** | `REQ-001`… | [specs/REQ-XXX.md](_template-feature-spec.md) | Contrato — spec, aceite, TDD |

**Desenvolvimento parte do card**, não diretamente do REQ.

## Um card pode ter vários REQs

**Sim** — quando entregam juntos (ex.: CARD-001 = REQ-001 login + REQ-002 sessão).

**Não** — se o card fica grande demais (revisão IA na descoberta).

## Um REQ pode ter várias funcionalidades?

**Sim**, se vertical slice coeso (ex.: CRUD de uma entidade).

## Quando criar novo REQ

- Contrato testável em poucas páginas
- Camadas de teste claras ([tdd-workflow.md](../testing/tdd-workflow.md))

## Quando agrupar REQs no mesmo card

- Mesmo PR / mesmo ciclo de dev
- Dependência forte entre REQs
- Mesma fase

## Quando separar cards

- Domínios independentes
- Entregas em fases diferentes
- PRs revisáveis separados

## Anti-padrões

- REQ no backlog **sem card**
- Card **sem fase**
- Card referenciando REQs de fases diferentes sem justificativa
- Um único REQ/card para "projeto inteiro"

## Rastreabilidade

1. REQ → ≥1 card → 1 fase
2. [traceability-matrix.md](../traceability-matrix.md): colunas Fase + Card
3. `./scripts/validate-planning.sh`

## Revisão IA

[req-validation-checklist.md](req-validation-checklist.md) — seções Fases e Cards.
