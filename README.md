# Modelo — Projeto base SDD + TDD + IA

Template de **governança de engenharia** para iniciar qualquer projeto com:

- **Spec-Driven Development (SDD)**
- **Test-Driven Development (TDD)**
- Protótipo **HTML mockado** (contrato visual)
- Regras para **IA na IDE** (Cursor Project Rules + Skills)
- Rastreio em **Markdown**, gates de **CI** e checklists de **segurança**

## Leia primeiro

**[INICIO.md](INICIO.md)** → **[docs/00-getting-started.md](docs/00-getting-started.md)** → **[docs/ESTRUTURA-DO-TEMPLATE.md](docs/ESTRUTURA-DO-TEMPLATE.md)**

## Comandos úteis (`make`)

```bash
make help              # lista alvos
make validate          # smoke local (template + hub + demo)
make ci                # validação estrita (≈ GitHub Actions)
make hub-build         # gera JSON da monitoria do projeto
make hub-serve         # Project Hub — template virgem (:8090)
make hub-demo-serve    # Project Hub — demo com dados (:8091)
```

Aliases legados (`metrics-serve`, `quality-serve`) redirecionam para o **Project Hub** (abas Processo e Qualidade).

## Como usar

1. Clone este repositório como **Modelo** (template upstream).
2. `make create-project NAME="Seu Produto" GIT_INIT=1` — cria pasta **irmã** (`../seu-produto`) com métricas isoladas e config de produto (`upstream_dev_mode: false`).
3. Abra a pasta irmã no Cursor e siga discovery → bootstrap (não desenvolva produto dentro de `Modelo/`).

> Enquanto a evolução do template não concluir, o Modelo mantém `upstream_dev_mode: true` para maintainers; produtos irmãos já nascem prontos para discovery.
4. Siga o [guia de início](docs/00-getting-started.md).
5. **Descoberta** via IA (skill `project-discovery`) — ideia, backlog, revisão de requisitos.
6. **Bootstrap** (skill `project-bootstrap`, blocos A–N).
7. Aprove protótipo HTML (se front) em `design-references/APPROVAL.md`.
8. Desenvolva features com spec aprovada + TDD (skill `feature-delivery`).

## MVP enxuto

O primeiro ciclo pode ser pequeno para validar a esteira: **1 spec + 1–2 telas HTML + 1 endpoint**. O bootstrap completo continua obrigatório; o inventário de telas/API cresce depois.

## Estrutura principal

Guia completo: **[docs/ESTRUTURA-DO-TEMPLATE.md](docs/ESTRUTURA-DO-TEMPLATE.md)** (pastas, arquivos, `project.config.yaml`, camadas).

```txt
INICIO.md                 # Entrada para humanos
AGENTS.md                 # Entrada para IA
project.config.yaml       # Config viva (preenchida no bootstrap)
docs/                     # Governança, specs, testes, segurança
design-references/        # Protótipo HTML mockado
.cursor/rules/            # Regras Cursor (enxutas)
.cursor/skills/           # Bootstrap e entrega de feature
templates/                # CI, hooks, docker, config schema
scripts/                  # Validação do template e config
```

## Regras Cursor vs Team vs User

| Tipo | Onde | Uso |
|------|------|-----|
| **Project Rules** | `.cursor/rules/` neste repo | Específico do produto |
| **Team Rules** | Cursor (organização) | Políticas da empresa |
| **User Rules** | Cursor (pessoal) | Preferências (idioma, tom) |

Não duplique gates do projeto em User Rules.

## Validar o template

```bash
chmod +x scripts/*.sh
./scripts/validate-template.sh
./scripts/validate-html-prototype.sh
./scripts/validate-config.sh
```

## Protótipo de exemplo

Telas demo em `design-references/screens/` (login → dashboard → item-form).  
Demo: `demo@exemplo.com` / `demo123`

```bash
cd design-references && python3 -m http.server 8080
# http://localhost:8080/screens/login.html
```

## Monitoria do projeto (Project Hub)

O **Project Hub** é o painel de **monitoria do projeto** integrado ao template Modelo. Ele consolida, em uma única interface HTML, o estado do seu produto ao longo do ciclo de vida — da descoberta até a entrega — sem depender de ferramentas externas de gestão.

**O que é:** um dashboard local gerado a partir dos artefatos que você já mantém no repositório (`project.config.yaml`, cards, specs, testes, checklists, timeline). Não é um produto SaaS nem um substituto de Jira/GitHub Issues; é a **visão unificada do método** para humanos e agentes de IA na IDE.

**O que faz:** lê a documentação e os arquivos de rastreio do repo, monta 12 JSON em `docs/meta/project-hub/data/` e renderiza seis áreas numa **UI premium SPA** (sidebar, tema claro/escuro, dados ao vivo via `hub-data.js`):

| Módulo | O que monitora |
|--------|----------------|
| **Overview** | Próximo passo sugerido, funil de fases (discovery → bootstrap → design → MVP → FASE-X), entregas por CARD, atividade recente, KPIs consolidados |
| **Processo** | Tempo humano / IA / ocioso por rodada, calendário, Gantt, forecast — fonte: `docs/meta/process-timeline.yaml` |
| **Qualidade** | Cobertura, TDD por REQ, gaps spec → teste, última execução de testes — fonte: specs + `quality-runs/` |
| **Segurança** | Checklist global de entrega, REQs sensíveis, threat model, lacunas LGPD — fonte: `docs/security/` + specs |
| **A11y** | Checklist WCAG e status de acessibilidade por tela mock — fonte: `design-references/APPROVAL.md` |
| **Design** | Readiness dos mocks HTML antes do framework de UI — fonte: `design-references/` + `project.config.yaml` |

**Como abrir:**

```bash
make hub-build && make hub-serve
# http://localhost:8090/project-hub/
```

Demo com massa de dados realista (5 REQs, timeline, gaps de segurança/a11y):

```bash
make hub-demo-serve
# http://localhost:8091/project-hub/
```

**Próximo passo automático:** o Overview exibe o prompt que agentes devem sugerir ao final de cada turno (rule `084-next-prompt`):

```bash
python3 scripts/resolve_next_step.py --root . --json
```

Documentação completa: **[docs/meta/project-hub.md](docs/meta/project-hub.md)** · matriz de cenários: [docs/meta/project-hub/demo-matrix.md](docs/meta/project-hub/demo-matrix.md).

**Protótipo exportável (FilaSaúde):** para apresentar o hub como mock de alta fidelidade (offline, com telas do produto de saúde), gere o ZIP:

```bash
bash scripts/build-filasaude-hub-prototype.sh
# → exports/FilaSaude-Project-Hub-prototipo.zip
```

## Evoluir o Modelo

Após cada **fase** entregue: retrospectiva em [docs/meta/retrospectives/](docs/meta/retrospectives/) (skill `phase-retrospective`). **Tempos de processo** (humano / IA / ocioso) alimentam o hub na aba Processo — ver [docs/meta/process-metrics.md](docs/meta/process-metrics.md). Ciclo de vida: [docs/00-project-lifecycle.md](docs/00-project-lifecycle.md). Após o projeto: export de benchmarks + [improving-the-template.md](docs/meta/improving-the-template.md).
