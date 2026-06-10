# Sugestões para o bootstrap (rascunho)

_Gerado na descoberta — confirmar nos blocos A–N do bootstrap. **Não iniciar bootstrap antes da aprovação de `vision-review.md`.__

---

## B — Stack (sugestão)

| Campo | Sugestão | Justificativa |
|-------|----------|---------------|
| **has_frontend** | `true` | Produto centrado na experiência mobile-first |
| **has_backend** | `true` | Ingestão de filas, adapters, cache, API pública |
| **has_database** | `true` | Hospitais, snapshots de fila, geo, auditoria |
| **frontend** | **Next.js 15** (App Router) + TypeScript | SSR/SEO para site público; PWA futuro; ecossistema maduro |
| **backend** | **Go 1.22+** (confirmado 2026-06-10) | FastAPI/NestJS descartados |
| **monorepo** | `true` (opcional) | Turborepo ou npm workspaces: `apps/web`, `apps/api`, `packages/shared` |
| **auth** | MVP público sem login; admin com auth simples (JWT/session) | Usuário final anônimo; painel interno protegido |

### CSS e UI

- **Tailwind CSS** + componentes headless (Radix/shadcn) — alinhado ao visual dos mockups
- **TanStack Query** — cache e refresh de filas no cliente

### Mapas e geo

| Serviço | Uso MVP | Observação |
|---------|---------|------------|
| **Google Maps Platform** | Maps JavaScript, Directions, Places (rating) | ~US$ 200/mês crédito gratuito — adequado para dev/MVP piloto |
| **PostGIS** | Busca por proximidade, bounding box | Backend |
| **Fallback** | Leaflet + OSM | Se custo/limites Google forem bloqueantes |

---

## C — Infra (sugestão)

| Item | Sugestão |
|------|----------|
| **Docker** | `docker-compose.yml`: web, api, postgres (+ postgis), redis |
| **DB** | PostgreSQL 16 + extensão PostGIS |
| **Migrations** | Alembic (FastAPI) ou Prisma/Drizzle (NestJS) |
| **Cache** | Redis — snapshots de fila (TTL 1–5 min), rotas frequentes |
| **Reverse proxy** | Traefik ou nginx (prod); dev expõe portas diretas |

### Modelo de dados (alto nível)

- `hospital` — id, nome, endereço, lat/lng, google_place_id, uf, ativo
- `specialty` — catálogo normalizado (Pediatria, Clínica Médica, …)
- `queue_snapshot` — hospital_id, specialty_id, risk_level, waiting_count, avg_wait_24h, avg_wait_7d, captured_at
- `data_source` — tipo, url, credenciais (vault), sla_minutes
- `integration_health` — source_id, hospital_id, last_ok_at, lag_minutes, status

### Pipeline de ingestão

- Job agendado (Celery/APScheduler ou cron) a cada **5 min** por fonte
- **Adapter pattern**: um módulo por fonte (DF TrakCare, API municipal SP, …)
- Normalização → persistência → invalidação de cache

---

## D — Testes (sugestão)

| Camada | Ferramenta |
|--------|------------|
| Unit back | pytest (FastAPI) ou Jest (NestJS) |
| Unit front | Vitest + Testing Library |
| Integração | pytest + Testcontainers (Postgres/Redis) |
| Contrato API | OpenAPI diff + schemathesis ou Dredd |
| Mutation | opcional pós-MVP |

Cobertura alvo: 90% (já em `project.config.yaml`).

---

## E — CI

| Campo | Sugestão |
|-------|----------|
| **platform** | GitHub Actions |
| Pipeline | lint → unit → integration → build Docker → (deploy manual MVP) |

---

## F — Contratos

| Campo | Sugestão |
|-------|----------|
| **contract_first** | `true` — OpenAPI em `docs/api/openapi.yaml` |
| **versioning** | `/api/v1/` — breaking changes incrementam major |

Endpoints MVP (rascunho):

- `GET /hospitals` — filtros: lat, lng, radius, specialty, uf, sort
- `GET /hospitals/{id}` — detalhe + snapshots recentes
- `GET /hospitals/compare` — ids + specialty
- `GET /integrations/status` — painel admin (auth)
- `GET /health` — liveness

---

## G — Observabilidade

- Logs estruturados (JSON) com `request_id`, `source_adapter`
- Métricas: lag de ingestão, hospitais stale, latência API, cache hit rate
- Alertas: integração down > 15 min, fila de ingestão parada

---

## H — Design (se front)

| Item | Sugestão |
|------|----------|
| **Telas MVP** | As 10 telas em `design-references/screens/` |
| **reference_root** | `design-references/screens/` (canônico pós bloco H) |
| **pattern_version** | 1 — mobile-first, cards, badges de risco (Manchester) |
| **Acessibilidade** | WCAG 2.1 AA como meta; contraste nos badges de risco |

---

## I — Segurança

- HTTPS obrigatório; headers de segurança (CSP para Maps)
- Rate limiting na API pública
- Admin: auth + RBAC mínimo
- Secrets em variáveis de ambiente / vault — nunca no repo
- LGPD: consentimento de geolocalização; política de retenção mínima
- Ver rule `050-security.mdc` na entrega

---

## J — Cards (bootstrap bloco J)

| Campo | Sugestão |
|-------|----------|
| **provider** | `markdown` (cards em `docs/tracking/cards/`) |
| **mirror_in_repo** | `true` |
| Notas | Cards e REQs só após **project-mvp-planning** |

---

## K — i18n

| Campo | Sugestão |
|-------|----------|
| **enabled** | `false` no MVP |
| **default_locale** | `pt-BR` |
| Evolução | es-ES se expandir fronteiras |

---

## L — E2E

| Campo | Sugestão |
|-------|----------|
| **enabled** | `true` (pós primeiras telas reais) |
| **tool** | Playwright |
| **critical_flows** | onboarding → mapa → detalhe → rota; comparar hospitais |

---

## M — Ambientes

- `local` — Docker Compose
- `staging` — dados simulados ou sandbox de integração
- `prod` — piloto regional

---

## N — LGPD

| Campo | Sugestão |
|-------|----------|
| **applies** | `true` |
| Dados | Localização (consentida), favoritos (local ou conta futura), logs agregados |
| Não coletar | Dados de saúde do usuário, identificação de pacientes nas filas |

---

## O — Entrega (commits, releases, automação IA)

| Campo | Sugestão |
|-------|----------|
| **commit.convention** | `conventional` |
| **release.strategy** | `semver_mvp` — `0.1.0` piloto |
| **agent_automation.run_tests_without_approval** | `false` (default) — manter até equipe definir |

---

## Justificativa (escala + mobile-first + restrições)

1. **Next.js + FastAPI/NestJS**: separação clara entre experiência pública (SSR, SEO “fila emergência [cidade]”) e API de ingestão/consulta.
2. **PostGIS + Redis**: proximidade geográfica e leitura intensiva de snapshots sem sobrecarregar fontes externas.
3. **Docker Compose**: atende pedido explícito; onboarding de dev em um comando.
4. **Google Maps (MVP gratuito)**: Directions + Places cobrem rota, tempo e rating; crédito mensal cobre piloto; monitorar billing.
5. **Adapter pattern**: única forma viável de escalar nacionalmente com fontes heterogêneas (DF hoje, outras UFs amanhã).
6. **Mockups HTML** em `design-references/` — validar UX antes do framework UI.

---

## Decisões confirmadas no bootstrap (2026-06-09)

- [x] **Go 1.22+** — backend (confirmado Romulo Canella, 2026-06-10)
- [x] **Next.js 15** — frontend (confirmado)
- [x] **MapLibre + OSM + OSRM na VM** — mapas MVP free
- [x] **GitHub Actions + deploy SSH na VM** — CI/CD
- [x] **Alertas MVP:** localStorage no cliente; push/backend na fase 2
