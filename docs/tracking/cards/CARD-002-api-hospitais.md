---
id: CARD-002
phase: FASE-1
status: open
title: API REST v1 hospitais
req_ids: [REQ-003]
specs: []
external_id: null
external_url: null
assignee: null
branch: null
pr: null
opened_at: null
done_at: null
---

# CARD-002 — API REST v1 hospitais

## Objetivo

Implementar API pública de hospitais conforme OpenAPI v0.1.0, com **segurança baseline** (rate limit, CORS, headers).

## REQs vinculados

| REQ_ID | Spec | Status spec |
|--------|------|-------------|
| REQ-003 | docs/specs/REQ-003-api-hospitais.md | draft |

## Escopo ampliado (REQ-003)

**Endpoints:** `GET /health`, `GET /api/v1/hospitals`, `GET /api/v1/hospitals/{id}`, `GET /api/v1/hospitals/compare`

**Segurança (MVP piloto):**

- Rate limiting na API pública (ex.: por IP, configurável via env)
- CORS restrito a origens permitidas (`APP_URL`, staging)
- Headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` (CSP na implementação web)

**Erros:** catálogo `docs/api/error-catalog.md`; respostas com `code` + `traceId`

## Critério de conclusão do card

- [ ] Spec REQ-003 approved
- [ ] Todos endpoints OpenAPI implementados + testes contrato/integração
- [ ] Rate limit retorna 429 documentado; CORS validado em teste

## Camadas TDD

| unit back | integração | contrato |
|-----------|------------|----------|
| handlers, validação params | PostGIS queries, Redis cache read | schemathesis / openapi diff |

## Notas

Depende de CARD-001. Referência: `docs/api/openapi.yaml`.
