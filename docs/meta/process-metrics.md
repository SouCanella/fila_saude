# Métricas de tempo do processo

Registro **transparente** de quanto tempo o projeto e cada **FASE** consomem, separando:

| Tipo | Significado |
|------|-------------|
| **Humano ativo** | Você no fluxo (prompt, revisão, espera desta resposta) |
| **IA (est.)** | Turno do agent — estimativa em v1 |
| **Ausente** | Gap entre rodadas/sessões acima do limiar (`idle_threshold_hours`) |

## Fonte da verdade

- [`process-timeline.yaml`](process-timeline.yaml) — edite ou peça à IA corrigir
- [`process-metrics-log.md`](process-metrics-log.md) — linha por evento (opcional, append-only)
- Painel: [`meta/process-metrics/index.html`](process-metrics/index.html) — ferramenta do **método Modelo** (não é mock de produto)

```bash
make deps                    # ou: pip install -r scripts/requirements-metrics.txt
make metrics-build           # ou: ./scripts/build-process-metrics.sh
make metrics-serve           # ou: ./scripts/serve-process-metrics.sh
make metrics-demo-serve      # demo com massa (porta 8091)
# Painel: http://localhost:8090/project-hub/
# Guia:  http://localhost:8090/project-hub/guide.html
# Demo:  examples/project-hub-demo/ (porta 8091 — build-project-hub-demo.sh)
```

Gráficos, médias por atividade, calendário, Gantt, tema claro/escuro, datas **pt-BR**, aba **Previsões**.

### Previsões ≠ datas de negócio

Eventos e barras **roxos / (est.)** = **projeção estatística**. **Não** são SLA nem promessa ao cliente. O painel exibe aviso destacado.

### Quando as previsões passam a valer

Só após `mvp_planning.status: complete` (backlog com fases/cards). Antes disso, o painel mostra sobretudo realizado (rodadas/marcos).

### Datas de entrega previstas

Na aba **Previsões**, cada card/fase exibe **entrega prevista (est.)** (`forecast_delivery_*`), alinhada ao Gantt. A tabela **Cronograma de entregas previstas** e o KPI **Entrega MVP (est.)** usam o mesmo encadeamento — sempre rotuladas como projeção estatística.

### Ritual a cada interação

1. Fim de turno relevante → skill **process-metrics** (rodada no YAML).
2. `./scripts/build-process-metrics.sh` → abrir painel.
3. Ao abrir/fechar card → `opened_at` / `done_at` no CARD MD.
4. Após planejamento MVP ou fase → marco + comparar aba Previsões (sempre rotulado **est.**).

### Datas de cards no Gantt

Prioridade: `opened_at` / `done_at` em `docs/tracking/cards/CARD-XXX.md`; fallback: rodadas no timeline.

## Legenda no painel

- **Azul** — tempo humano ativo (prompt, revisão, espera da resposta)
- **Verde** — tempo de IA (estimativa por rodada na v1)
- **Cinza** — ausente (intervalo entre rodadas acima do limiar)

A legenda global aparece no topo da aba **Visão geral** e **Por fase**; o donut de “Distribuição do projeto” repete os totais do projeto.

## Alerta `needs_review`

Uma ou mais rodadas em `process-timeline.yaml` têm `needs_review: true`. Isso significa que, ao registrar o turno, a IA **não tinha certeza** da fase, atividade ou card (contexto ambíguo). Não é erro do painel — é pedido de revisão humana: abra o YAML, ajuste `phase` / `activity` / `card_id`, depois `needs_review: false` e rode o build de novo. No **demo** (`examples/process-metrics-demo/`) há uma rodada de exemplo (`unknown`) para validar o ledger.

## Cobertura de testes

Este painel mede **tempo do processo** (governança), não cobertura de código. Use o **[Project Hub](project-hub/index.html)** (`make hub-serve`, aba `#quality`) para TDD, rastreio REQ → testes e última execução.

## Atribuição de fase (rodadas)

A IA usa o **resolver de contexto** (skill `process-metrics`):

1. `project.config.yaml` → `process_metrics.active_context`
2. Único card `in_progress`
3. Skill em execução (discovery → SETUP, feature-delivery → card.phase, etc.)
4. Gate do projeto (discovery/bootstrap/design)
5. Ambíguo → pergunta ou `needs_review: true` (amarelo no painel)

## Prompts úteis

**Definir contexto**

```
Contexto de métricas: CARD-003, FASE-1, implementation
```

**Início / fim de sessão**

```
Início sessão — implementação CARD-003
```

```
Fim sessão
```

**Corrigir registro**

```
Corrigir rodada round-2026-06-04T14-03: phase FASE-2, activity spec_refinement
```

## Transparência

Após cada registro a IA deve responder em **3 linhas**: o que gravou, fase/atividade, como abrir o painel.

Nada de métricas só em `.cursor/` — tudo versionado em `docs/meta/`.

## Config (`project.config.yaml`)

```yaml
process_metrics:
  enabled: true
  project_started_at: null
  idle_threshold_hours: 4
  ai_minutes_per_round_default: 3
  active_context:
    activity: null
    phase: null
    card_id: null
    set_at: null
```

## v2 (roadmap)

- Hooks Cursor para duração real da IA
- Export de chat para separar espera de resposta vs ausente
