# Delivery log

Registro de entregas.

---

## Entrega: CARD-001 — Fundação técnica

Status: Em andamento

Data/hora início: 2026-06-10 04:00  
Data/hora fim: —  
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

- Comando unitários: `cd apps/api && go test ./internal/...` — **green**
- Comando integração handler: `go test -tags=integration ./tests/integration/handler/...` — **green**
- Integração infra/DB: requer `docker compose up` (porta 5432 livre) + `DATABASE_URL` com `sslmode=disable`
- Red → Green: sim (unit + handler integration)
- Unitários back: config, domain, repository mock, middleware, health handler
- Integração: handler health/404; postgres/redis/osrm/repo — executar após compose local

### Checklist DoD

- [x] Specs approved
- [x] TDD unitários green
- [ ] Integração infra green (depende compose local — porta 5432 ocupada no ambiente agente)
- [x] OpenAPI /health implementado
- [ ] Cobertura >= threshold (medir após integração)
- [x] delivery-log e matrix atualizados
- [ ] Pipeline verde (CI com go test unit)

### Pendências

- [ ] Rodar `./scripts/smoke-compose.sh` com porta 5432 livre
- [ ] `go test -tags=integration ./tests/integration/...` com compose up
- [ ] Fechar CARD-001 após integração green

---
