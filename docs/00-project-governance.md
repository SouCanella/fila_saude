# Governança do projeto — SDD + TDD + IA

## 1. Objetivo

Este documento define as regras obrigatórias de desenvolvimento. Nenhuma funcionalidade está concluída só porque "funcionou localmente".

Ordem em projeto novo: **[DISCOVERY.md](DISCOVERY.md)** (fases + cards + REQs) → bootstrap → design (se front) → **card aberto** → specs approved → TDD → fechar card.

## 1b. Cards (obrigatórios)

- **Fase** → **Card** (unidade de trabalho) → **REQ** (spec/contrato)
- MD canônico: `docs/tracking/cards/` (`tracking.cards.mirror_in_repo: true`)
- Provider externo opcional (bootstrap J): Jira, Kanbanize, Azure DevOps, GitHub Issues
- Detalhe: [operations/issue-cards.md](operations/issue-cards.md)

---

## 2. Spec-Driven Development (SDD)

Antes de implementar qualquer funcionalidade:

- Objetivo e problema que resolve
- Escopo incluído e fora
- Regras de negócio
- Critérios de aceite testáveis
- Cenários de sucesso e erro
- Impactos em API, DB, front, segurança e testes
- Spec com `status: approved` (exceto hotfix em [operations/hotfix.md](operations/hotfix.md))

Template: [specs/_template-feature-spec.md](specs/_template-feature-spec.md)

---

## 3. Test-Driven Development (TDD)

Ciclo obrigatório: **Red → Green → Refactor**

1. Ler spec + plano de testes
2. Escrever ou atualizar testes
3. Confirmar falha esperada (red)
4. Implementar o menor código necessário (green)
5. Refatorar com testes verdes
6. Integração/contrato se API ou integração externa
7. Atualizar OpenAPI, docs e [delivery-log.md](delivery-log.md)

Detalhes: [testing/tdd-workflow.md](testing/tdd-workflow.md)

**Proibido:** código sem teste; remover ou enfraquecer testes para passar CI.

---

## 4. Definition of Ready (DoR)

Tarefa **não inicia** implementação (nem TDD) sem:

- [ ] Descrição e objetivo de negócio claros
- [ ] Critérios de aceite testáveis
- [ ] Regras de negócio e cenários sucesso/erro conhecidos
- [ ] Impacto técnico estimado (API, DB, front, segurança)
- [ ] Estratégia de teste esboçada: camadas marcadas na spec (unit back/front, integração, contrato, E2E se `critical_flow`)
- [ ] `critical_flow` confirmado pelo humano (define se E2E entra no plano)
- [ ] Dependências mapeadas
- [ ] Referência HTML existente ou planejada (se UI)
- [ ] Impacto OpenAPI identificado (se API)

---

## 5. Definition of Done (DoD)

- [ ] Implementação finalizada
- [ ] TDD seguido (evidência red→green no delivery-log)
- [ ] Testes unitários back e/ou front criados ou atualizados (conforme camadas da spec)
- [ ] Cobertura ≥ threshold em `project.config.yaml` (default 90%)
- [ ] Testes de integração/contrato para APIs afetadas
- [ ] E2E verde se `critical_flow: true` e `e2e.enabled: true`
- [ ] OpenAPI e [error-catalog.md](api/error-catalog.md) atualizados
- [ ] Segurança validada ([security/security-checklist.md](security/security-checklist.md))
- [ ] Threat model se `sensitive: true` na spec
- [ ] UI fiel ao HTML aprovado (`pattern_version` atual) se front
- [ ] Spec, [delivery-log.md](delivery-log.md), [traceability-matrix.md](traceability-matrix.md) atualizados
- [ ] Pipeline verde
- [ ] Sem dívida técnica **crítica** aberta ([tech-debt.md](tech-debt.md))

---

## 6. Modularidade

Aplicar: Separation of Concerns, SRP, Vertical Slice Architecture, Clean/Hexagonal (back), Component-Driven Development (front).

Gatilhos de revisão (não hard fail no CI):

- Arquivo > 300 linhas → avaliar divisão
- Função > 40 linhas → avaliar extração
- Regra de negócio não em controllers/views

---

## 7. Protótipo HTML vs TDD

| Fase | Objetivo | TDD |
|------|----------|-----|
| `design-references/` mockado | UX, fluxos, padrão visual | Não |
| `design.status: approved` | Travar tokens/components | Gate |
| Código real (framework) | Produção | **Obrigatório** |

Regra: se existe na spec do MVP, existe mockado e funcionando no HTML.

Mudança visual: propagar global, exceção com ADR, ou novo padrão — ver regra `071-ui-change-propagation`.

---

## 8. MVP enxuto

Primeiro ciclo pode ser **1 spec piloto + 1–2 telas HTML + 1 endpoint** para validar a esteira. Bootstrap completo continua obrigatório; telas/API podem crescer incrementalmente.

---

## 9. OpenAPI e contratos

OpenAPI em [api/openapi.yaml](api/openapi.yaml) é contrato oficial. Contract-first quando `openapi.contract_first: true`.

Sincronia mock/HTML: [testing/contract-sync.md](testing/contract-sync.md)

---

## 10. Segurança e LGPD

- Checklist por entrega: [security/security-checklist.md](security/security-checklist.md)
- Por tipo de mudança: [security/security-by-change-type.md](security/security-by-change-type.md)
- LGPD: [security/privacy-lgpd.md](security/privacy-lgpd.md)
- Issue crítica/alta bloqueia merge

---

## 11. Observabilidade

Logs estruturados: [observability/logging.md](observability/logging.md). Erro sem log útil é débito técnico.

---

## 12. Banco de dados

Alterações via migration versionada. Ver [database/migrations-policy.md](database/migrations-policy.md).

---

## 13. Pipeline mínimo

Gates em [../templates/ci/README.md](../templates/ci/README.md): lint, typecheck, unit, coverage, integração API, OpenAPI validate, contrato, segurança, build.

---

## 14. Melhoria contínua do processo

Ao concluir uma **fase** (todos os cards da `FASE-X` em `done`):

- Rodar retrospectiva curta (skill **phase-retrospective**)
- Registrar em [meta/retrospectives/](meta/retrospectives/) — `completed` ou `skipped` com motivo
- Soft gate: documentação obrigatória; **não** bloqueia a fase seguinte (regra `080-phase-retrospective`)

Foco: processo, governança, mocks, TDD, cards, CI, IA — não substitui ADR nem `delivery-log`.

Feedback ao template Modelo: agregar nas retros e, quando aplicável, [meta/improving-the-template.md](meta/improving-the-template.md).

### Ciclo de vida do projeto

Mapa oficial: [00-project-lifecycle.md](00-project-lifecycle.md) — visão → bootstrap/mocks → planejamento MVP → entrega.

### Métricas de tempo (transparentes)

- Fonte: [meta/process-timeline.yaml](meta/process-timeline.yaml) + skill **process-metrics**
- Painel: [meta/process-metrics/index.html](meta/process-metrics/index.html) (ferramenta do método; não é mock de produto)
- Benchmarks entre projetos: [meta/process-benchmarks/](meta/process-benchmarks/) + `./scripts/export-process-benchmark.sh`
- Três faixas: humano ativo | IA (estimativa v1) | ausente (derivado)
- Visões: **projeto** e **por fase** (`SETUP`, `FASE-1`, …)
- Não bloqueia entrega se métricas incompletas

---

## 15. Regra soberana

- Qualidade > velocidade
- Contrato do projeto > sugestão da IA
- Comportamento esperado esclarecido na spec antes de continuar se teste e implementação divergirem

Código sem rastreabilidade é dívida. Código sem teste é aposta.

---

## 16. IA na IDE

Copiloto técnico, não autoridade. Deve ler governance, spec aprovada e padrões existentes.

Resposta após entrega: arquivos (prod + testes), red/green, cobertura, docs, riscos, pendências.

Humanos: [00-getting-started.md](00-getting-started.md) | Agentes: [../AGENTS.md](../AGENTS.md)
