# Guia de início — passo a passo

Siga esta ordem **sem pular etapas** na primeira vez.

---

## 1. O que é este projeto base

Repositório de **governança** (SDD + TDD + IA), não uma aplicação pronta. Contém:

- Documentação e templates
- Regras para a IA (`.cursor/rules/`)
- Protótipo HTML mockado (`design-references/`)
- Configuração parametrizável (`project.config.yaml`)

---

## 2. Pré-requisitos

- Git
- [Cursor](https://cursor.com) ou IDE com contexto de projeto + IA
- Node.js e/ou Docker — **conforme stack escolhida no bootstrap**
- Navegador (para revisar protótipo HTML)

---

## 3. Como nascer o projeto (pasta irmã — recomendado)

**Um produto por Modelo** — métricas e atividade do hub ficam na pasta do produto, não no template upstream.

```bash
cd /caminho/Modelo          # pasta do template upstream
make create-project NAME="Fila Saúde" GIT_INIT=1
cd ../fila-saude            # nome = slug; ou use DIR= na criação
# Abra esta pasta no Cursor (File → Open Folder)
```

O script cria **`../<slug>`** (irmã de `Modelo`, mesmo diretório pai), copia o template, roda `init-new-project` + `reset-hub-activity`, define `template.is_upstream: false` e `project.name`.

| Comando | Função |
|---------|--------|
| `make create-project NAME="..."` | Cria pasta irmã + projeto virgem |
| `make create-project NAME="..." DIR=pasta` | Nome da pasta irmã explícito |
| `GIT_INIT=1` | `git init` na pasta nova (sem histórico do Modelo) |

**Alternativa manual** (legado, desencorajada): `cp -r Modelo ../meu-projeto` exige `make repair-product-config NAME="..."` antes de `init-new-project` (sem marcadores o init falha). Preferir `make create-project`.

**Atividade recente no hub:** em projeto virgem o feed fica **vazio** até rodada, entrega ou card ativo. Só métricas: `make reset-hub-activity`.

**Caminho com espaços:** use aspas no `cd` e em `NAME="..."`.

Discovery e bootstrap rodam **na pasta irmã**, não dentro de `Modelo/`.

**Documentação de configuração:** [operations/spawn-project.md](operations/spawn-project.md) (tabela `template.*`, vários produtos, `HUB_PORT`).

**Validar contexto:** `make validate-spawn-context`

---

## 4. Primeira abertura no Cursor

- Abra a **pasta irmã** do spawn (não o Modelo upstream para trabalho de produto).
- Rules, skills e fluxo vêm **na cópia** — `.cursor/rules/`, `.cursor/skills/`, `AGENTS.md` (não se perde o método).
- Skills em `.cursor/skills/` ficam disponíveis para a IA.
- `project.config.yaml` inicia com `bootstrap.status: incomplete`.

---

## 5. Primeira conversa (copiar e colar)

Use um prompt de [prompts/primeira-conversa.md](prompts/primeira-conversa.md).

**Projeto novo:** primeiro **Descoberta do projeto**, depois **Bootstrap**.

---

## 6. Ciclo de vida (mapa)

Guia único: **[00-project-lifecycle.md](00-project-lifecycle.md)** — ideia → mocks + arquitetura → planejamento MVP → entrega + métricas.

---

## 7. Fase 0 — Descoberta leve

Guia: **[DISCOVERY.md](DISCOVERY.md)**

| Você discute | A IA gera |
|--------------|-----------|
| Problema, visão, escopo MVP | `docs/discovery/product-discovery.md` |
| Stack sugerida | `docs/discovery/bootstrap-hints.md` |
| Confirmação humana | `docs/discovery/vision-review.md` |

Confirme **visão/escopo** antes de `discovery.status: complete`. **Não** exige cards/REQs nesta fase.

Depois: bootstrap (fase 1).

---

## 8. Fase 1 — Bootstrap (blocos A–O)

Guia completo: **[BOOTSTRAP.md](BOOTSTRAP.md)** — o que é, blocos A–O, prompts, gates.

**Tenha em mãos:** nome do produto, stack desejada, descrição do MVP, telas/fluxos (texto), requisitos de segurança.

| Bloco | Tema |
|-------|------|
| A | Identidade |
| B | Stack |
| C | Infra / DB |
| D | Testes |
| E | CI |
| F | OpenAPI / contratos |
| G | Logs |
| H | Design / HTML mock |
| I | Segurança |
| J | Rastreio e cards | Cards MD + provider externo |
| K | i18n |
| L | E2E (fluxos críticos) |
| M | Ambientes |
| N | LGPD |
| O | Entrega | Commits, releases, automação IA (testes) |

**Resultado:** `project.config.yaml` com `bootstrap.status: complete`, `docs/operations/commit-policy.md`, `docs/operations/release-policy.md` e docs gerados.

Tempo típico: 1–3 sessões de chat, dependendo do MVP.

---

## 9. Aprovação visual (se `has_frontend: true`)

1. Abra `design-references/screens/*.html` no navegador.
2. Navegue todos os fluxos — tudo deve funcionar (mock).
3. Preencha checklist em `design-references/APPROVAL.md`.
4. Na conversa: *"Aprovo o padrão visual"* → IA atualiza `design.status: approved`.

Sem aprovação: **não** inicie código do app (React, Vue, etc.).

---

## 10. Fase 2 — Planejamento executável do MVP

**Pré-requisitos:** `bootstrap.status: complete` e `design.status: approved` (se front).

Guia: skill **project-mvp-planning** + [00-project-lifecycle.md](00-project-lifecycle.md)

| Artefato | Função |
|----------|--------|
| `docs/planning/mvp-phases.md` | Fases FASE-X |
| `docs/backlog/mvp-backlog.md` | REQs |
| `docs/planning/cards-backlog.md` + `docs/tracking/cards/` | Cards |
| `docs/discovery/requirements-review.md` | Revisão IA |
| `docs/traceability-matrix.md` | Rastreio |

Gate: todo REQ em ≥1 card → `mvp_planning.status: complete`.

Validar: `./scripts/validate-planning.sh`

---

## 11. Fase 3 — Primeira feature

1. Copie `docs/specs/_template-feature-spec.md` → `docs/specs/REQ-001-nome.md`
2. Preencha DoR + plano de testes
3. Aprove spec (`status: approved`)
4. Abra card (`card-tracking`) → skill **feature-delivery** + TDD
5. PR + `delivery-log.md` + `traceability-matrix.md`

---

## 11.5 Retrospectiva por fase entregue

Quando **todos** os cards de uma `FASE-X` estiverem `done`:

1. Use a skill **phase-retrospective** (ou o prompt em `docs/prompts/primeira-conversa.md`).
2. Responda perguntas curtas (~5 min) sobre processo, mocks, TDD, regras e IA.
3. Documente em `docs/meta/retrospectives/FASE-X-retro.md` e atualize `index.md`.

**Soft gate:** retro preenchida **ou** skip explícito (`status: skipped` + motivo). Não bloqueia cards da fase seguinte; a IA avisa se faltar documentação.

Validação: `./scripts/validate-phase-retros.sh` (avisos).

---

## 11.6 Métricas de tempo do processo

Acompanhe **projeto inteiro** e **cada FASE**, separando tempo **humano ativo**, **IA (est.)** e **ausente** (gaps longos).

1. Dados em `docs/meta/process-timeline.yaml` (transparente, editável).
2. A IA registra rodadas/marcos (skill **process-metrics**) e resume em 3 linhas.
3. Gere o painel: `make hub-build`
4. Abra: `make hub-serve` → **Project Hub** http://localhost:8090/project-hub/ (aba **Processo**)

Guia: [`docs/meta/project-hub.md`](meta/project-hub.md) · métricas: [`docs/meta/process-metrics.md`](meta/process-metrics.md)

---

## 11.7 Saúde da qualidade (TDD + rastreio REQ)

Complementa métricas de **tempo** — foco em **cobertura por requisito** e última execução de testes.

1. Plano TDD nas specs (`Camadas de teste` + tabelas por camada).
2. `make quality-validate-specs` — coerência do plano.
3. `make quality-scaffold REQ=REQ-XXX` — stubs TDD red (tag `@req` nos testes).
4. Após suite: `export-quality-run.sh` ou `quality-runs/manual.yaml` → `make hub-build` (ver [ci-ritual](meta/project-hub/ci-ritual.md)).
5. Painel: `make hub-serve` → http://localhost:8090/project-hub/#quality

Demo: `make quality-demo-serve` (:8093). Guia: [`docs/meta/quality-health.md`](meta/quality-health.md)

---

## 12. Fluxo do dia a dia

| Quero… | Diga à IA… | Artefatos |
|--------|------------|-----------|
| Nova feature | Criar spec REQ-XXX, DoR, aguardar aprovação | `docs/specs/` |
| Implementar | Spec aprovada + feature-delivery + TDD | código + testes |
| Corrigir bug | Teste red → fix green | spec ou hotfix |
| Mudar API | OpenAPI primeiro | `docs/api/openapi.yaml` |
| Mudar UI | Atualizar HTML mock ou perguntar propagação | `design-references/` |
| Hotfix urgente | Seguir `docs/operations/hotfix.md` | ADR + delivery-log 24h |
| Fase entregue (todos cards done) | phase-retrospective ou pular com skip documentado | `docs/meta/retrospectives/` |
| Ver tempos / qualidade / segurança | Project Hub `make hub-serve` | `#process` · `#quality` · `#security` |
| Ver tempos / registrar sessão | process-metrics; Início/Fim sessão; Contexto CARD-XXX | `process-timeline.yaml` + hub |
| Ver qualidade / gaps TDD | quality-health; `make quality-scaffold` | specs + `quality-health.data.json` |

---

## 13. Mapa de documentos

| Tema | Caminho |
|------|---------|
| **Ciclo de vida** | `docs/00-project-lifecycle.md` |
| **Descoberta (fase 0)** | `docs/DISCOVERY.md` |
| **Bootstrap (config inicial)** | `docs/BOOTSTRAP.md` |
| Cards / issue tracking | `docs/operations/issue-cards.md` |
| Fatiar REQs e cards | `docs/specs/req-slicing.md` |
| **Estrutura do template** | `docs/ESTRUTURA-DO-TEMPLATE.md` |
| Governança | `docs/00-project-governance.md` |
| TDD | `docs/testing/tdd-workflow.md` |
| OpenAPI | `docs/api/` |
| Erros API | `docs/api/error-catalog.md` |
| Migrations | `docs/database/migrations-policy.md` |
| Segurança | `docs/security/` |
| Logs | `docs/observability/logging.md` |
| Dívida técnica | `docs/tech-debt.md` |
| Hotfix | `docs/operations/hotfix.md` |
| Exemplo completo | `docs/examples/flow-01-crud.md` |
| Retro por fase | `docs/meta/retrospectives/` |
| Project Hub | `docs/meta/project-hub.md` — processo, qualidade, security, a11y, design |
| Métricas de tempo | `docs/meta/process-metrics.md` + `process-timeline.yaml` |
| Saúde da qualidade | `docs/meta/quality-health.md` + `make quality-build` |

---

## 12. O que NÃO fazer

- Implementar sem spec aprovada
- Código sem teste (TDD)
- Alterar UI sem propagar padrão ou ADR
- Endpoint sem OpenAPI
- Secrets no git
- Pular descoberta e bootstrap em projeto novo (sem decisão explícita documentada)

---

## 13. Problemas comuns

**IA bloqueou implementação**  
→ Normal. Verifique `project.config.yaml`: discovery? bootstrap? design approved? spec approved?

**Quero só conversar sobre a ideia do produto**  
→ Use o prompt Descoberta; não é bootstrap ainda.

**Quero pular bootstrap (dev experiente)**  
→ Só com ADR + checklist manual; atualize config com cuidado.

**Gate de cobertura 90% falhou no front**  
→ Ver exclusões em `project.config.yaml` → `coverage.frontend.exclude`.

**Mock HTML com link quebrado**  
→ `./scripts/validate-html-prototype.sh`

---

## Próximo documento

Regras detalhadas: [00-project-governance.md](00-project-governance.md)
