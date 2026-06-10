# Project Hub — monitoria do projeto

Painel **unificado** do método Modelo. Uma URL local consolida processo, qualidade, segurança, acessibilidade e design.

## O que é

O **Project Hub** (monitoria do projeto) é a ferramenta de **observabilidade do processo de engenharia** embutida no template Modelo. Ele transforma artefatos já versionados no repositório — config, cards, specs, testes, checklists, timeline — em um **dashboard HTML interativo**.

Características:

- **Local e determinístico** — `make hub-build` regenera JSON a partir dos arquivos-fonte; não há API externa.
- **Alinhado à governança** — reflete gates reais (discovery, bootstrap, design approved, spec approved, TDD).
- **Para humano e IA** — o Overview expõe `next_step.prompt`, o mesmo texto que agentes devem sugerir (rule `084-next-prompt`).
- **Não substitui** issue tracker externo (GitHub/Jira) — complementa com visão do **método** e saúde técnica.

URL canônica após `make hub-serve`: `http://localhost:8090/project-hub/` (porta padrão).

**Vários produtos irmãos em paralelo:** `make hub-serve HUB_PORT=8092` na pasta de cada produto. Ver [spawn-project.md](../operations/spawn-project.md).

**Guia integrado:** botão **Guia** ou `#guide` — renderiza este arquivo (`project-hub.md`) no shell premium, com índice lateral, tabelas e blocos de código.

### UI premium (padrão desde a migração)

O hub canônico usa **shell SPA premium** (sidebar, health ring, glass cards, tema claro/escuro):

| Arquivo | Papel |
|---------|--------|
| `index.html` | Layout premium + `#contentRoot` |
| `hub-premium.js` | Navegação hash (`#overview`, `#process`, …), Overview, Sec/A11y/Design |
| `hub-data.js` | `fetch` dos 12 JSON após `make hub-build` |
| `premium.css` | Visual premium (origem: `FilaSaude-Project-Hub-monitoria-premium-mockups/`) |
| `premium-bridge.css` | Harmoniza módulos legados `pm-*` / `qh-*` no shell |
| `legacy-templates.js` | Markup de Processo/Qualidade sem topbar |
| `hub.js` | Shim `ProjectHub.init` → `ProjectHubPremium.init` |

**Processo** e **Qualidade** montam `process-metrics.js` e `quality-health.js` **integralmente** dentro do shell (sem iframe). Botão **Atualizar** chama `POST /api/refresh` e recarrega JSON.

## O que faz

### Por módulo

| Módulo | Função | Fontes principais | Saída útil |
|--------|--------|-------------------|------------|
| **Overview** | Visão executiva do projeto | `hub.data.json`, `journey.data.json`, `delivery.data.json` | Próximo passo, funil de fases, entregas por CARD, feed de atividade, KPIs (health score, gaps, fases) |
| **Processo** | Métricas de tempo do trabalho | `process-timeline.yaml`, `delivery-log.md`, cards | Calendário de rodadas, Gantt, tempo humano vs IA vs ocioso, forecast por fase |
| **Qualidade** | Saúde TDD e cobertura por REQ | `docs/specs/`, `traceability-matrix.md`, `quality-runs/` | Última execução (pass/fail), gaps spec→teste, cobertura back/front vs threshold |
| **Segurança** | Postura de segurança por entrega | `docs/security/security-checklist.md`, frontmatter `sensitive` nas specs | % checklist, REQs sensíveis sem threat model, compliance LGPD |
| **A11y** | Acessibilidade dos mocks HTML | `design-references/APPROVAL.md`, `design.screens` no config | Checklist WCAG, status parcial/pendente por tela |
| **Design** | Prontidão visual antes do framework UI | `design-references/`, `APPROVAL.md`, `design.status` | Telas com mock, links para HTML, gate `approved` |

### No Overview (além das abas)

1. **Banner spawn** (`hub-spawn-banner`) — quando `hub.data.json` → `template.is_upstream` e `template.upstream_dev_mode` (Modelo em evolução do template); orienta `make create-project` para produto novo
2. Banner showcase (`hub-showcase-banner`) — projeto sem REQs no backlog (`data_mode` ≠ `real`)
3. **Próximo passo** — fase, skill, blockers, prompt copiável (`spawn` informativo no upstream com dev mode; bloqueante sem dev mode)
4. **Funil de fases** — discovery → bootstrap → design → mvp_planning → FASE-X
5. **Entregas** — CARD, REQ, gaps de qualidade, TDD red/green
6. **Atividade recente** — timeline, delivery-log, mtimes de artefatos
7. **KPIs** — OpenAPI, tech debt, release, retro pendente, benchmarks

### KPIs do header (topbar)

| Indicador | Origem | Como é calculado |
|-----------|--------|------------------|
| **Fase atual** | `hub.data.json` → `kpis.current_phase_id` | `build_project_journey.py`: primeira fase do funil com `status: in_progress` em `journey.data.json` → `lifecycle.phases` |
| **cards** (`2/6`) | `hub.data.json` → `delivery_completed` / `delivery_total` | `delivery.data.json` — cards com status `done` vs total no backlog |
| **gaps** (`4`) | `quality_gaps` + `security_gaps` | Soma em `build_hub_overview.py`: `quality.data.json` → `report.gap_count` (REQs sem cobertura TDD nas camadas da spec) **+** `security.data.json` → `report.gap_count` (threat model ausente, checklist global, etc.) |

No shell premium, **gaps** é um link: `#quality/gaps` abre o módulo Qualidade na aba **Riscos e gaps**; o tooltip do pill detalha a divisão qualidade/segurança. Gaps só de segurança apontam para `#security`.

### O que não faz

- Não executa testes (apenas exibe resultados exportados).
- Não abre/edita cards ou specs (somente leitura visual).
- Não envia notificações nem integra CI remota automaticamente (CI valida JSON via `make ci`).

## Comandos

```bash
make hub-build
make hub-serve      # http://localhost:8090/project-hub/
make hub-demo-serve # demo :8091 — examples/project-hub-demo/
```

Resolver próximo passo (JSON):

```bash
python3 scripts/resolve_next_step.py --root . --json
```

## Dados

| JSON | Builder |
|------|---------|
| `data/hub.data.json` | `build_hub_overview.py` (inclui `template.*`, `next_step`) |
| `data/process.data.json` | `build_process_metrics.py` |
| `data/quality.data.json` | `build_quality_health.py` |
| `data/security.data.json` | `build_security_health.py` |
| `data/a11y.data.json` | `build_accessibility_health.py` |
| `data/design.data.json` | `build_design_readiness.py` |
| `data/delivery.data.json` | `build_delivery_history.py` |
| `data/learning.data.json` | `build_retro_benchmark.py` |
| `data/journey.data.json` | `build_project_journey.py` |
| `data/tech_debt.data.json` | `build_tech_debt_health.py` |
| `data/openapi.data.json` | `build_openapi_health.py` |
| `data/release.data.json` | `build_release_health.py` |

Manifesto de artefatos monitorados: [project-artifacts.yaml](project-artifacts.yaml).

### Template virgem vs demo

| `make hub-serve` (este repo) | `make hub-demo-serve` (FilaSaúde) |
|------------------------------|-----------------------------------|
| Backlog/specs **reais** do projeto — sem fallback para `hub-showcase/` | `project.config.demo.yaml` + dados em `examples/project-hub-demo/` |
| `process-timeline.yaml` vazio até registrar rodadas | Timeline e entregas preenchidas para demo |
| `data_mode: showcase` = projeto sem REQs no backlog (banner no Overview) | `data_mode: real` |

REQs de exemplo (Login, Checkout) ficam só em `docs/examples/hub-showcase/` para testes/scripts — não entram no hub do template.

Rebuild após alterar documentação: `make hub-build` (ver [ci-ritual.md](project-hub/ci-ritual.md)).

## Quando usar

| Momento | Ação |
|---------|------|
| Após bootstrap / planejamento MVP | `hub-build` + conferir funil e próximo passo |
| Durante entrega de CARD | Aba Qualidade (gaps) + Overview (entregas) |
| Após rodada de testes | `export-quality-run.sh` ou `quality-runs/manual.yaml` → `hub-build` |
| Após turno de agente | Registrar round em `process-timeline.yaml` (skill `process-metrics`) → `hub-build` |
| Antes de aprovar UI | Abas Design + A11y |
| Antes de merge sensível | Aba Segurança |
| Demo / apresentação | `hub-demo-serve` ou ZIP FilaSaúde (abaixo) |

## Protótipo exportável (FilaSaúde)

Para compartilhar o hub como **protótipo HTML de alta fidelidade** (offline, tema saúde, mocks do produto):

```bash
bash scripts/build-filasaude-hub-prototype.sh
# → exports/FilaSaude-Project-Hub-prototipo.zip
```

O ZIP contém o mesmo hub (Overview + 5 módulos) com dados demo personalizados para **FilaSaúde** e telas mock (`login`, painel da fila, triagem). Ver README dentro do pacote.

## Validação e cenários

- Validação mestre: `make hub-validate-complete`
- Checklist humano: [VALIDATION-CHECKLIST.md](project-hub/VALIDATION-CHECKLIST.md)
- Matriz template vs demo: [demo-matrix.md](project-hub/demo-matrix.md)

Sync opcional cards ↔ GitHub: `./scripts/sync-card-github.sh open CARD-XXX --dry-run`.

Após testes no CI: `export-quality-run.sh` → `build-project-hub.sh`. Detalhe: [ci-ritual.md](project-hub/ci-ritual.md).

Config: `project.config.yaml` → `project_hub`

## Relação com painéis legados

`process-metrics/` e `quality-health/` como URLs isoladas estão **deprecated**. O hub monta esses módulos nas abas **Processo** e **Qualidade** (SPA, sem iframe). `index.html` legado redireciona para `#process` / `#quality`. Aliases `make metrics-serve` e `make quality-serve` redirecionam para o hub.

**Origem do design premium:** pasta `FilaSaude-Project-Hub-monitoria-premium-mockups/` na raiz do repo (referência histórica). Fonte de verdade pós-migração: `docs/meta/project-hub/`.
