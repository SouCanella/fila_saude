---
id: REQ-001
title: Monorepo e Docker
status: approved
approved_at: "2026-06-10T04:30:00Z"
approved_by: Romulo Canella
req_kind: non_functional
critical_flow: false
sensitive: false
card_ids: [CARD-001]
openapi_operations: []
mock_screens: []
visual_reference: null
---

# REQ-001 — Monorepo e Docker

## Objetivo

Estabelecer a fundação do repositório monorepo (Go + Next.js) e ambiente local reproduzível via Docker Compose com PostGIS, Redis e OSRM, desbloqueando desenvolvimento e deploy na VM.

## Escopo incluído

- Estrutura monorepo: `apps/api` (Go 1.22+), `apps/web` (Next.js 15), `packages/shared`
- `docker-compose.yml` com serviços: `postgres` (PostGIS 16), `redis` (7), `osrm` (profile `routing`)
- `.env.example` documentando variáveis obrigatórias (DB, Redis, OSRM URL, portas)
- README ou seção em `docs/operations/environments.md` com comando local: `docker compose up postgres redis osrm`
- CI GitHub Actions scaffold: jobs lint/test placeholders para `apps/api` e `apps/web`
- `go.mod` / `package.json` raiz com workspaces npm

## Escopo fora

- Implementação completa da API de negócio (CARD-002)
- Deploy produção na VM (documentado, não automatizado neste REQ)
- Build de imagem OSRM com dados OSM completos do Brasil (MVP: serviço compose healthy ou stub documentado)
- Frontend funcional além de scaffold mínimo

## Regras de negócio

- Portas padrão: web 3000, api 8000, postgres 5432, redis 6379, osrm 5000 (conforme `docs/02-architecture.md`)
- Serviços de infra devem subir independentemente da API (dev local sem build Go)
- Secrets nunca commitados; `.env` no `.gitignore`

## Critérios de aceite

- [ ] `docker compose up -d postgres redis osrm` sobe os três serviços com healthcheck OK
- [ ] Estrutura `apps/api`, `apps/web`, `packages/shared` existe com README mínimo por app
- [ ] `.env.example` cobre DATABASE_URL, REDIS_URL, OSRM_BASE_URL, APP_PORT
- [ ] Workflow CI dispara em push/PR (lint ou test placeholder verde)
- [ ] Documentação local atualizada com comandos de subida

## Cenários de sucesso

1. Desenvolvedor clona repo, copia `.env.example` → `.env`, sobe compose e conecta ao Postgres via psql
2. CI passa em branch feature sem código de produto ainda implementado

## Cenários de erro

1. Porta 5432 ocupada → compose falha com mensagem clara (documentar override via `.env`)
2. OSRM sem dados → healthcheck pode falhar; documentar profile `routing` ou imagem pré-configurada para dev

## DoR checklist

- [x] Objetivo claro
- [x] Aceite testável
- [x] Cenários erro definidos
- [x] Impacto técnico estimado
- [x] Estratégia de teste (camadas conforme [../testing/tdd-workflow.md](../testing/tdd-workflow.md))
- [x] `critical_flow` definido (false — sem E2E)
- [x] Dependências mapeadas (nenhuma — primeiro REQ)
- [ ] HTML mock (n/a — infra)
- [ ] OpenAPI (n/a — sem endpoint novo além de scaffold futuro)

## Camadas de teste

- [ ] Unitário back (domínio / use case) — mínimo: validação config se loader existir
- [ ] Unitário front (componente / hook) — n/a
- [x] Integração API (compose sobe, conectividade) — **principal**
- [ ] E2E — n/a (`critical_flow: false`)

## Plano de testes (TDD)

### Unitários — back

| Caso | Arquivo teste | Status |
|------|---------------|--------|
| Config carrega env obrigatórias ou falha explícita | `apps/api/internal/config/config_test.go` | pending |
| Valores default de portas quando env ausente | `apps/api/internal/config/config_test.go` | pending |

### Unitários — front

| Caso | Arquivo teste | Status |
|------|---------------|--------|
| n/a | — | n/a |

### Integração (infra / compose)

| Endpoint / fluxo | Cenários (sucesso + erros doc) | Arquivo teste | Status |
|------------------|--------------------------------|---------------|--------|
| Postgres PostGIS | Conexão + extensão postgis habilitada | `apps/api/tests/integration/infra/postgres_test.go` | pending |
| Redis | PING retorna PONG | `apps/api/tests/integration/infra/redis_test.go` | pending |
| OSRM | GET /health ou route stub responde | `apps/api/tests/integration/infra/osrm_test.go` | pending |
| Compose smoke | Script ou teste documentado `docker compose ps` healthy | `scripts/smoke-compose.sh` ou CI job | pending |

### E2E

| Fluxo de negócio | Persona | Passos (resumo) | Resultado esperado | Arquivo teste | Status |
|------------------|---------|-----------------|--------------------|---------------|--------|
| n/a | — | — | — | — | n/a |

## Impactos

- API: scaffold `cmd/server` mínimo (opcional neste REQ; health em REQ-014)
- DB: Postgres PostGIS via compose
- Front: scaffold Next.js vazio
- Segurança / LGPD: `.env.example` sem secrets reais
- Observabilidade: n/a (REQ-014)

## Threat model

Não aplicável (`sensitive: false`).
