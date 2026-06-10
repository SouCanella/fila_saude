# Comece aqui

Este repositório é um **projeto base de governança** para desenvolvimento com **SDD**, **TDD** e **IA na IDE** (Cursor ou similar). Não é uma aplicação pronta — é o manual operacional, regras e templates.

## Próximo passo

Leia o passo a passo completo:

**[docs/00-getting-started.md](docs/00-getting-started.md)**

## Primeira conversa com a IA

Copie um prompt de **[docs/prompts/primeira-conversa.md](docs/prompts/primeira-conversa.md)** e cole no chat da IDE.

**Projeto novo:** na pasta **Modelo** upstream → `make create-project NAME="..." GIT_INIT=1` (pasta **irmã**) → abrir irmã no Cursor → **Descoberta** → **Bootstrap** → **Planejamento MVP** → entrega. Mapa: [docs/00-project-lifecycle.md](docs/00-project-lifecycle.md).

**Nota:** o Modelo upstream pode ter `upstream_dev_mode: true` durante a evolução do template; o produto na pasta irmã nasce com config de produto (sem dev mode).

## Mapa rápido

| Preciso de… | Arquivo |
|-------------|---------|
| Passo a passo inicial | [docs/00-getting-started.md](docs/00-getting-started.md) |
| **Spawn pasta irmã (Fase −1)** | [docs/operations/spawn-project.md](docs/operations/spawn-project.md) |
| **Ciclo de vida** | [docs/00-project-lifecycle.md](docs/00-project-lifecycle.md) |
| **Descoberta (fase 0)** | [docs/DISCOVERY.md](docs/DISCOVERY.md) |
| **O que é bootstrap / como usar** | [docs/BOOTSTRAP.md](docs/BOOTSTRAP.md) |
| **Pastas, arquivos e config** | [docs/ESTRUTURA-DO-TEMPLATE.md](docs/ESTRUTURA-DO-TEMPLATE.md) |
| **Cards (obrigatório)** | [docs/operations/issue-cards.md](docs/operations/issue-cards.md) |
| Fatiar fases / cards / REQs | [docs/specs/req-slicing.md](docs/specs/req-slicing.md) |
| Regras completas do projeto | [docs/00-project-governance.md](docs/00-project-governance.md) |
| Instruções para agentes de IA | [AGENTS.md](AGENTS.md) |
| Configuração do projeto (após bootstrap) | [project.config.yaml](project.config.yaml) |
| Protótipo visual HTML | [design-references/](design-references/) |
| Spec de feature | [docs/specs/_template-feature-spec.md](docs/specs/_template-feature-spec.md) |
| Entregas e rastreio | [docs/delivery-log.md](docs/delivery-log.md) |
| **Monitoria do projeto (Project Hub)** | [docs/meta/project-hub.md](docs/meta/project-hub.md) — `make hub-serve` |

## Ordem resumida

1. Copiar este repo para o seu projeto
2. Abrir no Cursor
3. **Descoberta leve** — visão e escopo (`project-discovery`)
4. **Bootstrap** + protótipo HTML + aprovação (se front)
5. **Planejamento MVP** — fases, cards, REQs (`project-mvp-planning`)
6. Abrir card → specs approved → TDD (skills `card-tracking` + `feature-delivery`)
