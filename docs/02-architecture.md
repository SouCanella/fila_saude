# Arquitetura — FilaSaúde Brasil

_Atualizado com confirmação humana — bloco B (2026-06-10)._

---

## Decisões de stack (confirmadas)

| Decisão | Escolha | Alternativa descartada |
|---------|---------|------------------------|
| Backend | **Go 1.22+** | FastAPI, NestJS |
| Frontend | **Next.js 15** (App Router) + TypeScript | Vite SPA — SEO menos prioritário |
| Monorepo | **Sim** — npm workspaces (`apps/web`, `apps/api`) | — |
| Mapas MVP | **MapLibre + OpenStreetMap + OSRM** (VM) | Google Maps — custo/billing |
| Deploy | **VM** + Docker Compose; CI GitHub Actions | PaaS |
| Alertas MVP | **localStorage** no cliente | Push/backend — fase 2 |
| Auth usuário final | Nenhuma (público) | — |
| Auth admin | JWT + RBAC mínimo | — |

---

## Stack

| Camada | Tecnologia |
|--------|------------|
| Web | Next.js 15, React 19, TypeScript, Tailwind CSS, Radix/shadcn, TanStack Query |
| API | Go, chi ou echo, pgx, sqlc (ou repository manual) |
| DB | PostgreSQL 16 + PostGIS |
| Cache | Redis 7 |
| Migrations | goose ou atlas |
| Ingestão | goroutines + robfig/cron (MVP) |
| Roteamento mapa | OSRM self-hosted na VM (dados OSM) |
| Testes back | go test, testify, testcontainers-go |
| Testes front | Vitest, React Testing Library |
| Contrato | OpenAPI 3.1 + oapi-codegen ou ogen |
| E2E | Playwright |
| CI | GitHub Actions (lint/test/build) → deploy SSH na VM |
| Observabilidade | slog/zap (JSON), request_id, métricas Prometheus-ready |

---

## Estrutura de pastas (monorepo)

```
fila_saude/
├── apps/
│   ├── web/                 # Next.js — UI pública + admin
│   └── api/                 # Go — REST + jobs ingestão
│       ├── cmd/server/
│       ├── internal/
│       │   ├── domain/
│       │   ├── adapters/    # um módulo por fonte externa
│       │   ├── repository/
│       │   ├── handler/     # HTTP v1
│       │   └── jobs/
│       └── migrations/
├── packages/
│   └── shared/              # Tipos TS compartilhados (front)
├── docs/
├── design-references/
├── tests/e2e/
├── docker-compose.yml
└── project.config.yaml
```

---

## Infraestrutura

### Docker Compose (local + VM)

Serviços: `web`, `api`, `postgres` (PostGIS), `redis`, `osrm` (profile routing).

| Serviço | Porta |
|---------|-------|
| web | 3000 |
| api | 8000 |
| postgres | 5432 |
| redis | 6379 |
| osrm | 5000 |

Produção: **nginx/Caddy** na VM, HTTPS (Let's Encrypt), deploy manual via SSH (`docker compose pull && up -d`).

---

## Banco de dados

| Entidade | Campos principais |
|----------|-------------------|
| `hospital` | id, nome, endereço, lat/lng (PostGIS), rating_manual, uf, ativo |
| `specialty` | catálogo normalizado |
| `queue_snapshot` | hospital_id, specialty_id, risk_level, waiting_count, avg_wait_24h, avg_wait_7d, captured_at |
| `data_source` | tipo, url, credenciais (vault), sla_minutes |
| `integration_health` | source_id, hospital_id, last_ok_at, lag_minutes, status |

### Pipeline de ingestão

1. Job a cada **5 min** por fonte (cron)
2. **Adapter pattern** — módulo por fonte
3. Normalização → persistência → invalidação cache Redis (TTL 1–5 min)

---

## Autenticação

| Superfície | MVP |
|------------|-----|
| API pública | Sem auth; rate limiting |
| Admin | JWT Bearer + RBAC mínimo |
| Web | Anônimo; geolocalização com consentimento |

---

## Integrações externas

| Serviço | Uso |
|---------|-----|
| OpenStreetMap | Tiles (via MapLibre) |
| OSRM | Rota e tempo estimado |
| PostGIS | Proximidade no backend |
| Fontes de fila | Adapters por UF/município |

Rating MVP: seed/manual ou fonte pública — sem Google Places no piloto free.

---

## Referências

- Contrato API: [api/openapi.yaml](api/openapi.yaml)
- Testes: [testing/test-strategy.md](testing/test-strategy.md)
- Ambientes: [operations/environments.md](operations/environments.md)
