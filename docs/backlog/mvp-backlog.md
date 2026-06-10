# Backlog MVP — FilaSaúde Brasil

_Planejamento fase 2 — 2026-06-10 (rev. melhorias auditoria). Todo REQ em ≥1 card._

| REQ_ID | Fase | Card_ID | Título | Escopo (1 linha) | Prioridade | req_kind | critical_flow | Depende de | Objetivo |
|--------|------|---------|--------|------------------|------------|----------|---------------|------------|----------|
| REQ-001 | FASE-1 | CARD-001 | Monorepo e Docker | `apps/web`, `apps/api`, compose PostGIS+Redis+**OSRM** (profile routing), CI scaffold, `.env.example` | P0 | non_functional | false | — | O3 |
| REQ-002 | FASE-1 | CARD-001 | Schema e migrations | Entidades hospital, specialty, queue_snapshot, goose/atlas, PostGIS | P0 | functional | false | REQ-001 | O2 |
| REQ-003 | FASE-1 | CARD-002 | API REST v1 hospitais | GET health, hospitals (list+filtros), **/{id}**, compare; **rate limit**, **CORS**, security headers; OpenAPI contract-first | P0 | functional | false | REQ-002 | O1, O2 |
| REQ-004 | FASE-1 | CARD-003 | Adapter mock RJ | Seed 13 hospitais; filas Manchester; **`rating` simulado** (campo estático, sem Google Places); job 5 min; cache Redis | P0 | functional | false | REQ-002, REQ-003 | O2, O3 |
| REQ-005 | FASE-2 | CARD-004 | Shell Next.js + design system | Layout, nav, tokens Tailwind, a11y base (skip, focus) | P0 | functional | false | REQ-003 | O4 |
| REQ-006 | FASE-2 | CARD-005 | Onboarding e localização | Consentimento geo, endereço manual, especialidade, aviso médico/SAMU | P0 | functional | true | REQ-005 | O1, O4 |
| REQ-007 | FASE-2 | CARD-005 | Mapa, lista e início | **index** landing SSR; mapa MapLibre; lista; filtros; ranking; estados UI | P0 | functional | true | REQ-003, REQ-005 | O1 |
| REQ-008 | FASE-2 | CARD-006 | Detalhe hospital | Filas Manchester, 24h/7d, fonte, frescor, **rating simulado exibido** | P0 | functional | true | REQ-007 | O1, O2 |
| REQ-009 | FASE-2 | CARD-006 | Comparar hospitais | Matriz 2–3 unidades por especialidade | P1 | functional | true | REQ-007 | O1 |
| REQ-010 | FASE-2 | CARD-007 | Rota OSRM + MapLibre | Tempo/distância via OSRM (compose CARD-001); aviso SAMU | P0 | functional | true | REQ-001, REQ-008 | O1 |
| REQ-011 | FASE-2 | CARD-008 | Favoritos e alertas | localStorage; criar alerta simulado | P2 | functional | false | REQ-005 | O1 |
| REQ-012 | FASE-2 | CARD-008 | Sobre, LGPD e avisos | Copy legal; não substituir triagem; SAMU | P0 | non_functional | false | REQ-005 | O1 |
| REQ-013 | FASE-3 | CARD-009 | Admin integrações | **Login admin** (JWT/session); GET /integrations/status; painel admin; RBAC admin/viewer | P1 | functional | false | REQ-004 | O2 |
| REQ-014 | FASE-1 | CARD-001 | Observabilidade API | slog JSON, request_id, /health, métricas básicas ingestão | P1 | non_functional | false | REQ-001 | O2 |
| REQ-015 | FASE-3 | CARD-010 | E2E fluxos críticos | Playwright: 4 fluxos do config | P1 | non_functional | true | REQ-010 | O1 |

**Notas de escopo (auditoria 2026-06-10):**

- **Rating:** simulado no seed (REQ-004), exibido no front (REQ-008) — Google Places **fora do MVP**.
- **OSRM:** serviço no Docker Compose (REQ-001), consumido por REQ-010.
- **Segurança API pública:** rate limit + CORS + headers em REQ-003 (sem card extra).
- **CARD-005:** mantido único (10 cards) — ver `requirements-review.md`.

**Specs (draft — aprovar antes de implementar):** uma spec por REQ em `docs/specs/`

Ver [../planning/cards-backlog.md](../planning/cards-backlog.md) · [../traceability-matrix.md](../traceability-matrix.md).
