---
id: CARD-001
phase: FASE-1
status: done
title: Fundação técnica
req_ids: [REQ-001, REQ-002, REQ-014]
specs:
  - docs/specs/REQ-001-monorepo-docker.md
  - docs/specs/REQ-002-schema-migrations.md
  - docs/specs/REQ-014-observabilidade-api.md
external_id: null
external_url: null
assignee: null
branch: feature/CARD-001-fundacao-tecnica
pr: null
opened_at: "2026-06-10T04:00:00Z"
done_at: "2026-06-10T13:00:00Z"
---

# CARD-001 — Fundação técnica

## Objetivo

Monorepo Go + Next.js, Docker Compose (PostGIS, Redis, **OSRM**), migrations e observabilidade base da API.

## REQs vinculados

| REQ_ID | Spec | Status spec |
|--------|------|-------------|
| REQ-001 | docs/specs/REQ-001-monorepo-docker.md | **approved** · done |
| REQ-002 | docs/specs/REQ-002-schema-migrations.md | **approved** · done |
| REQ-014 | docs/specs/REQ-014-observabilidade-api.md | **approved** · done |

## Critério de conclusão do card

- [x] Specs dos REQs com `status: approved`
- [x] Estrutura monorepo + compose (PostGIS, Redis, OSRM stub)
- [x] Migrations + domain/repository
- [x] Logs JSON com request_id; `/health` retorna 200
- [x] `make test-api` + `make test-api-integration` green (Postgres :5433 se :5432 ocupada)

## Evidência testes

```bash
make test-api
POSTGRES_PORT=5433 docker compose up -d postgres redis
OSRM_PORT=5001 docker compose --profile routing up -d osrm
export DATABASE_URL='postgresql://filasaude:filasaude@localhost:5433/filasaude?sslmode=disable'
export REDIS_URL=redis://localhost:6379/0 OSRM_BASE_URL=http://localhost:5001
make test-api-integration
```
