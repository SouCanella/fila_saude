# Prompts — primeira conversa

Copie e cole no chat da IDE (Cursor ou similar). Cada bloco é um prompt pronto para uma fase do trabalho.

**Detalhe e regras completas:** [INICIO.md](../../INICIO.md) · [docs/00-getting-started.md](../00-getting-started.md) · [docs/00-project-governance.md](../00-project-governance.md)

**Spawn (Fase −1):** [docs/operations/spawn-project.md](../operations/spawn-project.md) · `make create-project`  
**Descoberta:** [docs/DISCOVERY.md](../DISCOVERY.md) · skill `project-discovery`  
**Cards:** [docs/operations/issue-cards.md](../operations/issue-cards.md) · skill `card-tracking`

---

## Contexto (leia antes de colar)

Este repositório é um **projeto base de governança**, não uma aplicação pronta. A ideia é desenvolver **com ajuda da IA**, de forma **organizada**, com **qualidade verificável** e **rastreabilidade auditável**.

| Pilar | O que garante |
|-------|----------------|
| **SDD** | Spec com critérios de aceite testáveis e `status: approved` antes de codificar produto |
| **TDD** | Teste **antes** (red) → código mínimo (green) → refactor; bug vira teste permanente |
| **Contratos** | OpenAPI + HTML mock aprovado = fonte da verdade |
| **Cards** | Fase → Card → REQ; MD versionado obrigatório; dev a partir do card |
| **Rastreabilidade** | Fase → Card → REQ → spec → testes → PR → matrix + delivery-log |
| **Confiança pós-dev** | Suite completa verde (CI + cobertura) — nada que já passava pode quebrar em silêncio |

A IA deve seguir [AGENTS.md](../../AGENTS.md) e as rules em `.cursor/rules/`. **Não pule gates:** spawn (pasta irmã) → descoberta leve → bootstrap → design aprovado → planejamento MVP → card → spec → TDD.

---

## Fase −1 — Spawn (obrigatório se estiver no Modelo upstream)

```
Quero iniciar o produto [NOME]. Estou na pasta Modelo upstream.

1. Rode make create-project NAME="[NOME]" GIT_INIT=1 (cria pasta IRMÃ ../slug — ver docs/operations/spawn-project.md)
2. Mostre o caminho absoluto criado
3. Peça para eu abrir ESSA pasta no Cursor (File → Open Folder) — não continuar no Modelo
4. Não preencha discovery nem mocks até eu confirmar que abri a pasta irmã
```

---

## Descoberta do projeto (fase 0 — na pasta do produto)

```
Estou na pasta do produto (spawn, .modelo-product-workspace ou template.is_upstream: false).

Tenho uma ideia de produto: [descreva em texto livre — objetivo, usuários, mobile-first, escala, MVP].

Use a skill project-discovery. Visão e escopo antes do bootstrap — ainda não execute bootstrap, planejamento de cards/REQs nem código de produto.

1. Explore tópico a tópico (objetivo, usuários/escala, plataformas, restrições, MVP narrativo, stack sugerida)
2. Preencha docs/discovery/product-discovery.md, bootstrap-hints.md, vision-review.md
3. Rascunho opcional docs/01-product-vision.md
4. Aguarde minha confirmação em vision-review.md antes de discovery.status: complete

Fases, REQs e cards: depois do bootstrap e mocks — prompt "Planejamento MVP".
```

---

## Planejamento MVP (após bootstrap + mocks aprovados)

```
Bootstrap e mocks estão prontos. Planeje o MVP executável para entrega.

Use a skill project-mvp-planning. Pré-requisitos: bootstrap.status: complete; design.status: approved (se has_frontend).

1. Fases em docs/planning/mvp-phases.md
2. REQs em docs/backlog/mvp-backlog.md
3. Cards em docs/planning/cards-backlog.md + docs/tracking/cards/CARD-XXX.md
4. requirements-review.md + traceability-matrix.md
5. ./scripts/validate-planning.sh
6. Aguarde minha confirmação antes de mvp_planning.status: complete
7. build-process-metrics.sh — projeções no painel são estatísticas, não datas de negócio

Gate: todo REQ em ≥1 card.
```

---

## Validar requisitos e rastreabilidade

```
Revise requisitos e rastreabilidade do projeto.

Use docs/specs/req-validation-checklist.md. Leia mvp-phases.md, cards-backlog.md, mvp-backlog.md, traceability-matrix.md, docs/tracking/cards/.

1. Atualize requirements-review.md (fases, cards, lacunas, rastreabilidade)
2. Corrija REQ sem card, card sem fase, fase sem cards
3. Rode ./scripts/validate-planning.sh e ./scripts/validate-traceability.sh
4. Liste ações — aguarde minha decisão (aceito/rejeito/adiado) nas propostas

Não implementar código de produto nesta revisão.
```

---

## Projeto novo (bootstrap)

```
Este é um projeto novo baseado no template Modelo (governança SDD + TDD + IA — não é app pronto).

Pré-requisito: discovery.status: complete (vision-review confirmado) OU discovery.skipped: true. Planejamento de REQs/cards é depois (project-mvp-planning).

Execute o bootstrap usando a skill project-bootstrap, bloco por bloco (A–N).
Faça perguntas em lotes de 5–8, não tudo de uma vez.

Leia primeiro: project.config.yaml, artefatos em docs/discovery/ e docs/backlog/mvp-backlog.md (se descoberta feita), AGENTS.md e docs/00-getting-started.md.
Confirme/refine sugestões da descoberta nos blocos A e B em vez de perguntar do zero.

Não implemente código de produto até:
1. project.config.yaml com bootstrap.status: complete
2. Se houver frontend: protótipo HTML em design-references/ com fluxos mockados e design.status: approved

No bootstrap, configure também testes, CI e comando de suite completa (regressivo) conforme a stack escolhida.
```

---

## Retomar bootstrap

```
Leia project.config.yaml e liste quais seções ainda estão pending.
Continue o bootstrap de onde parou (skill project-bootstrap).
Não implemente código de produto enquanto bootstrap.status != complete.
```

---

## Aprovar padrão visual

```
Revisei o protótipo HTML no navegador. Aprovo o padrão visual.

Atualize design-references/APPROVAL.md, project.config.yaml (design.status: approved, approved_at, approved_by) e confirme pattern_version.
```

---

## Nova feature (dia a dia)

```
Quero implementar [descreva a feature].

Siga SDD — ainda não codifique produto:

1. Crie ou atualize a spec em docs/specs/REQ-XXX-nome.md (copie _template-feature-spec.md)
2. Preencha DoR completo: objetivo, critérios de aceite testáveis, regras de negócio, impactos (API, DB, front, segurança)
3. Marque as camadas de teste na spec (unit back, unit front, integração, contrato, E2E) usando a matriz em docs/testing/tdd-workflow.md
4. Pergunte-me se este fluxo é critical_flow (E2E obrigatório) antes de fechar o plano de testes
5. Preencha o plano de testes por camada (tabelas back / front / integração / E2E)
6. Registre o REQ em docs/traceability-matrix.md (status: spec) e alinhe com docs/backlog/mvp-backlog.md
7. Execute subconjunto de docs/specs/req-validation-checklist.md (seção 8) e resuma lacunas antes de pedir aprovação
8. Aguarde minha aprovação explícita da spec (status: approved) antes de qualquer implementação
```

---

## Abrir card (iniciar trabalho)

```
Abra o card CARD-XXX para desenvolvimento.

Use skill card-tracking. Verifique specs dos req_ids estão approved.
1. Card status → in_progress; branch feature/CARD-XXX-slug
2. Atualize cards-backlog.md e arquivo MD do card
3. Se provider externo configurado: criar/sincronizar issue (docs/operations/issue-cards.md)
```

---

## Implementar card (TDD)

```
O card CARD-XXX está in_progress. Specs dos REQs linkados estão approved.

Use feature-delivery para implementar todos os REQs deste card com TDD estrito.
Siga docs/testing/tdd-workflow.md. Ao terminar cada REQ, atualize matrix; ao terminar todos, use prompt Fechar card.
```

---

## Atualizar card

```
Atualize o card CARD-XXX: [status / PR / assignee / notas].

Skill card-tracking. Sincronize MD canônico e ferramenta externa se configurada.
```

---

## Fechar card

```
Feche o card CARD-XXX — entrega concluída.

Skill card-tracking. Confirme DoD de todos REQs linkados.
1. Card status → done; delivery-log (entrada CARD-XXX)
2. Matrix atualizada; fechar issue externa se houver
3. Rodar regressivo conforme prompt Fechar entrega
```

---

## Aprovar spec e implementar (TDD estrito — REQ único)

```
A spec docs/specs/REQ-XXX-nome.md está aprovada (status: approved).

Use a skill feature-delivery. TDD estrito — nesta ordem:

1. Ler spec + DoR + camadas de teste marcadas + plano por camada
2. Atualizar docs/traceability-matrix.md (status: in progress)
3. Seguir a ordem em docs/testing/tdd-workflow.md (OpenAPI → unit back → integração/contrato → unit front → E2E se critical_flow)
4. Escrever ou atualizar testes PRIMEIRO e confirmar falha esperada (red) — sem implementar produto ainda
5. Implementar o menor código necessário (green) → refactor com testes verdes
6. Se API: OpenAPI + error-catalog + testes integração/contrato
7. Se UI: fiel ao HTML aprovado (pattern_version atual)
8. Se critical_flow: E2E conforme plano na spec
9. Segurança conforme docs/security/security-checklist.md

Ao terminar a implementação, NÃO considere a feature pronta — use o prompt "Fechar entrega" abaixo.
```

---

## Métricas — contexto e sessão

```
Contexto de métricas: CARD-003, FASE-1, implementation
```

```
Início sessão — [descrição curta, ex. implementação CARD-003]
```

```
Fim sessão
```

```
Abrir/atualizar painel: `make hub-build && make hub-serve` → http://localhost:8090/project-hub/#process (legado: `./scripts/build-process-metrics.sh`)
```

---

## Retrospectiva da FASE-X

```
Todos os cards da FASE-X estão done (ver docs/planning/cards-backlog.md).

Use a skill phase-retrospective:
1. Confirme que não há cards open/in_progress nesta fase
2. Faça as 6 perguntas curtas do template docs/meta/retrospectives/_template-fase-retro.md (um turno)
3. Gere docs/meta/retrospectives/FASE-X-retro.md e atualize index.md (status: completed)

Se eu quiser pular a retro: registre status skipped, skipped_reason e skipped_at no mesmo arquivo e no index — não bloqueie a próxima fase.
```

---

## Fechar entrega (antes do PR)

```
A implementação de REQ-XXX está concluída. Feche a entrega conforme DoD:

1. Rodar suite completa (regressivo): unit back + unit front + integração/contrato + E2E se critical_flow — tudo verde
2. Cobertura do módulo ≥ threshold em project.config.yaml; reportar comando e %
3. Atualizar docs/delivery-log.md: evidência red→green, arquivos alterados (prod + testes), riscos
4. Atualizar docs/traceability-matrix.md: testes, OpenAPI, PR, status done
5. Atualizar spec se algo mudou na implementação
6. Pipeline/CI verde; pendências não críticas → docs/tech-debt.md

Responda com: arquivos alterados, evidência de testes, cobertura, impacto OpenAPI/HTML/DB, riscos e pendências.
```

---

## Rodar regressivo

```
Execute a suite completa de testes do projeto (regressivo):

- Unitários (back e front, se aplicável)
- Integração e contrato OpenAPI (se API)
- E2E nos fluxos critical_flow (se configurado no bootstrap)

Reporte: comando(s) executados, resultado (pass/fail), cobertura se disponível, e lista de falhas com causa provável.

Se algo que já passava quebrou, pare — não considere a entrega pronta até corrigir e rerodar verde.
```

---

## Corrigir bug (TDD)

```
Bug: [descreva o comportamento incorreto e como reproduzir].

1. Escreva um teste que reproduza o bug (red)
2. Corrija com o menor diff possível (green)
3. Confirme que o teste permanece no regressivo
4. Atualize delivery-log.md; spec ou hotfix conforme docs/operations/hotfix.md se urgente
```

---

## Ajuste visual

```
Preciso ajustar [elemento visual] em [tela].

Antes de alterar: pergunte se devo propagar para todas as telas, aplicar só nesta tela (ADR) ou definir novo padrão global.
Se mudar padrão global: atualizar design-references/ e, se necessário, HTML mock antes do código do framework.
```

---

## Mapa rápido — qual prompt usar?

| Situação | Prompt |
|----------|--------|
| Ideia nova / visão ampla do produto | Descoberta do projeto (leve) |
| Mocks prontos, planejar MVP | Planejamento MVP |
| Revisar fases, cards, backlog | Validar requisitos e rastreabilidade |
| Abrir trabalho | Abrir card |
| Specs approved, implementar card | Implementar card |
| Spec única (legado) | Aprovar spec e implementar |
| Card pronto | Fechar card |
| FASE entregue (todos cards done) | Retrospectiva da FASE-X |
| Ver tempos do projeto / fase | Project Hub `#process` — `make hub-serve` |
| Atualizar status/PR do card | Atualizar card |
| Descoberta feita, configurar stack | Projeto novo (bootstrap) |
| Bootstrap interrompido | Retomar bootstrap |
| HTML mock pronto para validar | Aprovar padrão visual |
| Ideia nova ou mudança de escopo | Nova feature |
| Spec já aprovada, hora de codar | Aprovar spec e implementar |
| Código pronto, validar antes do PR | Fechar entrega |
| Só quero garantir que nada quebrou | Rodar regressivo |
| Bug em produção ou staging | Corrigir bug |
| Mudança só de UI | Ajuste visual |
