---
id: CARD-001
phase: FASE-1
status: in_progress
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
done_at: null
---

# CARD-001 — Fundação técnica

## Objetivo

Monorepo Go + Next.js, Docker Compose (PostGIS, Redis, **OSRM**), migrations e observabilidade base da API.

## REQs vinculados

| REQ_ID | Spec | Status spec |
|--------|------|-------------|
| REQ-001 | docs/specs/REQ-001-monorepo-docker.md | **approved** |
| REQ-002 | docs/specs/REQ-002-schema-migrations.md | **approved** |
| REQ-014 | docs/specs/REQ-014-observabilidade-api.md | **approved** |

## Critério de conclusão do card

- [x] Specs dos REQs com `status: approved`
- [x] Estrutura monorepo + compose (PostGIS, Redis, OSRM stub)
- [x] Migrations + domain/repository scaffold
- [x] Logs JSON com request_id; `/health` retorna 200
- [ ] Testes integração infra green (compose local — ver delivery-log)

## Camadas TDD (por REQ)

| REQ | unit back | integração | contrato |
|-----|-----------|------------|----------|
| REQ-001 | config ✅ | compose (manual) | — |
| REQ-002 | domain/repos ✅ | migrations (compose) | — |
| REQ-014 | middleware ✅ | /health ✅ | — |

## Notas

Implementação CARD-001 em andamento. Unit tests green. Integração DB requer `docker compose up` (porta 5432 livre).

**Branch:** `feature/CARD-001-fundacao-tecnica`
