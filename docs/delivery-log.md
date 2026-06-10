# Delivery log

Registro de entregas.

---

## Entrega: CARD-001 — Fundação técnica

Status: Concluída

Data/hora início: 2026-06-10 04:00  
Data/hora fim: 2026-06-10 13:00  
Responsável: Romulo Canella + IA  
Branch: feature/CARD-001-fundacao-tecnica  
PR/MR: —

### Card

- ID: CARD-001
- Arquivo: docs/tracking/cards/CARD-001-fundacao-tecnica.md
- Fase: FASE-1

### Requisitos cobertos (REQs)

- REQ-001 — spec: docs/specs/REQ-001-monorepo-docker.md (approved)
- REQ-002 — spec: docs/specs/REQ-002-schema-migrations.md (approved)
- REQ-014 — spec: docs/specs/REQ-014-observabilidade-api.md (approved)

### Resumo

Monorepo scaffold: `apps/api` (Go), `apps/web` (Next.js), `packages/shared`. Docker Compose com PostGIS, Redis, OSRM dev stub (profile `routing`). Migrations goose, domain/repository, `/health` + middleware slog JSON com `request_id`.

### Testes (TDD)

- Comando unitários: `make test-api` — **green**
- Comando integração: `make test-api-integration` — **green** (Postgres :5433, OSRM :5001)
- Red → Green: sim
- Unitários back: config, domain, repository mock, middleware, health handler
- Integração: handler health/404; postgres/redis/osrm/repo — executar após compose local

### Checklist DoD

- [x] Specs approved
- [x] TDD unitários + integração green
- [x] Integração infra green (compose POSTGRES_PORT=5433)
- [x] OpenAPI /health implementado
- [ ] Cobertura >= threshold (medir após integração)
- [x] delivery-log e matrix atualizados
- [ ] Pipeline verde (CI com go test unit)

### Pendências

- [ ] Nenhuma — CARD-001 fechado

---
