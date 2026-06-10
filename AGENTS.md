# AGENTS.md — Instruções para agentes de IA

> **Humanos:** leia [INICIO.md](INICIO.md) primeiro. Este arquivo é para agentes.

## Documentos obrigatórios

1. [docs/00-project-lifecycle.md](docs/00-project-lifecycle.md) — ciclo de vida completo
2. [docs/00-getting-started.md](docs/00-getting-started.md) — passo a passo
3. [docs/DISCOVERY.md](docs/DISCOVERY.md) — fase 0 (visão leve)
4. [docs/operations/issue-cards.md](docs/operations/issue-cards.md) — cards obrigatórios
5. [docs/ESTRUTURA-DO-TEMPLATE.md](docs/ESTRUTURA-DO-TEMPLATE.md) — pastas, config
6. [project.config.yaml](project.config.yaml) — discovery, bootstrap, mvp_planning, tracking.cards

## Primeira ação

**Fase −1 Spawn:** [docs/operations/spawn-project.md](docs/operations/spawn-project.md) — produto novo: `make create-project NAME="..." GIT_INIT=1` no Modelo → abrir **pasta irmã** no Cursor (rules/skills vêm na cópia). Cópia manual legada: `make repair-product-config NAME="..."`. Upstream sem `upstream_dev_mode`: não gravar discovery/mocks de produto no Modelo.

**Discovery pendente:** skill **project-discovery** → visão + `vision-review.md` → `discovery.status: complete`.

**Bootstrap pendente:** skill **project-bootstrap** (A–O); bloco **J** = `tracking.cards.provider`; bloco **O** = commits, releases, `agent_automation`.

**Planejamento MVP pendente:** após bootstrap + design approved → **project-mvp-planning** → fases, REQs, cards → `mvp_planning.status: complete`.

**Implementar:** card `in_progress` + specs approved → **feature-delivery** → fechar card (**card-tracking**).

**Fase entregue:** cards da `FASE-X` `done` → **phase-retrospective**.

## Fluxo (resumo)

Visão → bootstrap → mocks → planejamento MVP → Card → REQ → spec approved → TDD → retro

## Skills

| Skill | Quando |
|-------|--------|
| `project-discovery` | Visão e escopo (fase 0) |
| `project-bootstrap` | Stack A–N; mocks |
| `project-mvp-planning` | Fases, cards, REQs, review (após mocks) |
| `card-tracking` | Abrir, atualizar, fechar CARD-XXX |
| `feature-delivery` | Implementar REQs de card in_progress |
| `phase-retrospective` | Retro ao concluir FASE-X |
| `process-metrics` | Rodadas, marcos; resumo 3 linhas |
| `quality-health` | TDD, last-run, gaps REQ → testes |
| `project-hub` | Painel unificado + next_step |
| `process-benchmark` | Export benchmarks entre projetos |

## Automação (testes)

- `agent_automation.run_tests_without_approval` em `project.config.yaml` — ver rule `085-agent-automation`
- Commits/releases: [docs/operations/commit-policy.md](docs/operations/commit-policy.md), [release-policy.md](docs/operations/release-policy.md)

## Onde criar artefatos

| Artefato | Caminho |
|----------|---------|
| Fases | `docs/planning/mvp-phases.md` |
| Índice cards | `docs/planning/cards-backlog.md` |
| Card MD | `docs/tracking/cards/CARD-XXX.md` |
| REQ backlog | `docs/backlog/mvp-backlog.md` |
| Spec | `docs/specs/REQ-XXX-nome.md` |
| Painel métricas | `docs/meta/project-hub/` (#process) + `build-project-hub.sh` |
| Painel qualidade | `docs/meta/project-hub/` (#quality) + `make hub-build` |
| Benchmarks | `docs/meta/process-benchmarks/` + `export-process-benchmark.sh` |

## Comandos qualidade (atalho)

```bash
make quality-validate-specs   # plano TDD ↔ camadas na spec
make quality-scaffold REQ=REQ-001
make hub-build && make hub-serve   # Project Hub unificado
```

## Cards meta (repo Modelo)

Evolução do template usa IDs **slug** (`CARD-Hub-Evolucao`, `REQ-Hub-PoC-Ready`) e fase `SETUP`, indexados em `cards-backlog.md` na seção **Meta** — fora do fluxo discovery→MVP. Projetos reais continuam com `CARD-001` / `REQ-001` numéricos.

## Regra soberana

Contrato do projeto (spec, card MD, OpenAPI, HTML, testes) **vence** sugestões da IA.
