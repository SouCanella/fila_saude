# Estratégia de testes — FilaSaúde Brasil

Preenchida no bootstrap (bloco D — 2026-06-09).

## Pirâmide

1. **Unitários** (back + front) — maioria dos testes
2. **Integração API + contrato** — 100% endpoints documentados na OpenAPI
3. **E2E** — fluxos com `critical_flow: true` (Playwright)

**Qual camada por REQ:** matriz e ordem TDD em [tdd-workflow.md](tdd-workflow.md). Plano detalhado na spec (`_template-feature-spec.md`).

## Frameworks

| Camada | Ferramenta | Path |
|--------|------------|------|
| Back unit | go test + testify | `apps/api/internal/.../*_test.go` |
| Front unit | Vitest + Testing Library | `apps/web/tests/unit/` |
| API integração | go test + testcontainers-go | `apps/api/tests/integration/` |
| Contrato OpenAPI | openapi diff + testes HTTP contra spec | `apps/api/tests/contract/` |
| E2E | Playwright | `tests/e2e/` |

## Cobertura

Threshold **90%** em back e front — ver `project.config.yaml` → `coverage`.

Exclusões front documentadas no config (`.d.ts`, configs, generated).

## Matriz API (endpoint × cenários)

| Método | Path | Sucesso | Erros doc | SLA | Contrato |
|--------|------|---------|-----------|-----|----------|
| GET | `/health` | 200 | — | p99 < 50ms | sim |
| GET | `/api/v1/hospitals` | 200 lista | 400 params | p99 < 300ms | sim |
| GET | `/api/v1/hospitals/{id}` | 200 detalhe | 404 | p99 < 200ms | sim |
| GET | `/api/v1/hospitals/compare` | 200 matriz | 400 ids | p99 < 400ms | sim |
| GET | `/api/v1/integrations/status` | 200 painel | 401, 403 | p99 < 500ms | sim |

## Matriz E2E (fluxos críticos)

| Fluxo | Spec | Cenário | Status |
|-------|------|---------|--------|
| Onboarding → mapa | REQ futuro | Permite localização, exibe hospitais | pendente |
| Mapa → detalhe | REQ futuro | Clique card abre detalhe com filas | pendente |
| Detalhe → rota | REQ futuro | Ver rota exibe tempo/distância | pendente |
| Comparar hospitais | REQ futuro | Seleciona 2+ unidades, matriz | pendente |

## Mutation testing

**Desabilitado no MVP** — reavaliar pós-estabilização da API de ingestão.

## CI

Pipeline GitHub Actions: lint → unit → integration → contrato → build Docker → export quality run.

Ver `.github/workflows/ci.yml`.
