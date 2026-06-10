# Fases do MVP — FilaSaúde Brasil

_Planejamento executável — fase 2 (2026-06-10). Stack: Go + Next.js + PostGIS + OSM/OSRM._

| Fase | Objetivo | Ordem | Critério de conclusão | Retro | Cards |
|------|----------|-------|------------------------|-------|-------|
| **FASE-1** | Fundação técnica e dados piloto RJ | 1 | API v1 documentada; 13 hospitais mock no DB; Docker Compose sobe local | Após CARD-003 | CARD-001 … CARD-003 |
| **FASE-2** | Experiência cidadão mobile-first | 2 | 10 telas mock replicadas em Next.js; fluxos mapa→detalhe→rota; favoritos local | Após CARD-008 | CARD-004 … CARD-008 |
| **FASE-3** | Operação, confiança e qualidade | 3 | Admin integrações protegido; E2E dos 4 fluxos críticos passando | Após CARD-010 | CARD-009 … CARD-010 |

---

## FASE-1 — Fundação técnica e dados piloto RJ

**Objetivo:** monorepo, infra Docker, schema PostGIS, API Go contract-first, ingestão mock dos 13 hospitais RJ.

**Entregáveis:**
- `docker compose up` (postgres+postgis, redis, api)
- OpenAPI `docs/api/openapi.yaml` implementada (health + hospitals)
- Seed/mock adapter alimentando snapshots de fila

**Critério de done:** `./scripts/validate-openapi.sh` + testes integração API verdes; dados RJ consultáveis via API.

---

## FASE-2 — Experiência cidadão mobile-first

**Objetivo:** replicar mockups aprovados em Next.js consumindo API real (ou mock server em dev).

**Entregáveis:**
- Layout, tokens, navegação
- Onboarding, mapa, lista, detalhe, comparar, rota
- Favoritos/alertas (localStorage) + páginas legal/LGPD

**Critério de done:** paridade visual com `design-references/`; TanStack Query refresh; estados loading/erro/vazio.

---

## FASE-3 — Operação, confiança e qualidade

**Objetivo:** painel admin de integrações, auth JWT, E2E Playwright dos fluxos críticos.

**Entregáveis:**
- `/api/v1/integrations/status` + tela admin
- Suite E2E: onboarding→mapa, mapa→detalhe, detalhe→rota, comparar

**Critério de done:** admin protegido; E2E verde no CI (placeholder até scaffold).

---

## Fora do MVP (FASE-4+)

- Login usuário final, push notifications, PWA instalável
- Integração real DF/municipal sem contrato
- Google Maps / Places (MVP usa OSM + OSRM)
- App nativo, pagamentos, i18n

Ver [../backlog/mvp-backlog.md](../backlog/mvp-backlog.md) · [cards-backlog.md](cards-backlog.md).
