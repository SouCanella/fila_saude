---
id: REQ-014
title: Observabilidade API
status: approved
approved_at: "2026-06-10T04:30:00Z"
approved_by: Romulo Canella
req_kind: non_functional
critical_flow: false
sensitive: false
card_ids: [CARD-001]
openapi_operations:
  - getHealth
mock_screens: []
visual_reference: null
---

# REQ-014 — Observabilidade API

## Objetivo

Garantir logs estruturados JSON, correlação por `request_id` e endpoint `/health` conforme OpenAPI, base para operação e métricas futuras de ingestão.

## Escopo incluído

- Logger `slog` (JSON) em stdout
- Middleware HTTP: gera/propaga `X-Request-ID` (UUID v4); inclui method, path, status, duration_ms, request_id em cada log
- `GET /health` → 200 `{"status":"ok"}` conforme `docs/api/openapi.yaml` (`HealthResponse`)
- Scaffold servidor Go mínimo (`cmd/server`) registrando middleware + rota health
- Stub ou comentário para métricas Prometheus (`/metrics` opcional, não obrigatório no MVP piloto)
- Documentação: campos de log esperados em `docs/operations/` ou README api

## Escopo fora

- Rate limiting, CORS (REQ-003)
- Métricas de negócio de ingestão (CARD-003)
- APM/tracing distribuído (Jaeger, etc.)
- Alerting produção

## Regras de negócio

- Todo request HTTP gera exatamente um log de conclusão (nível info para 2xx/3xx, warn para 4xx, error para 5xx)
- Se cliente envia `X-Request-ID` válido, reutilizar; senão gerar novo
- `/health` não exige auth; não consulta DB no MVP (liveness simples)

## Critérios de aceite

- [ ] `GET /health` retorna 200 e body `{"status":"ok"}`
- [ ] Response inclui header `X-Request-ID`
- [ ] Log JSON contém: `request_id`, `method`, `path`, `status`, `duration_ms`, `level`, `msg`
- [ ] Testes unitários do middleware passam
- [ ] Teste integração HTTP valida health + header

## Cenários de sucesso

1. curl `/health` → 200 + request_id no header e no log
2. Request com `X-Request-ID: abc-123` → mesmo id no response e log

## Cenários de erro

1. Rota inexistente → 404 com log warn e request_id
2. Panic recuperado (se handler configurado) → 500 com log error — opcional no scaffold

## DoR checklist

- [x] Objetivo claro
- [x] Aceite testável
- [x] Cenários erro definidos
- [x] Impacto técnico estimado
- [x] Estratégia de teste
- [x] `critical_flow: false`
- [x] Dependências: REQ-001 (scaffold api + compose)
- [ ] HTML mock (n/a)
- [x] OpenAPI: `GET /health` já definido

## Camadas de teste

- [x] Unitário back (middleware logger, request_id)
- [ ] Unitário front — n/a
- [x] Integração HTTP `/health` (sem contrato formal schemathesis neste REQ — assert manual alinhado OpenAPI)
- [ ] E2E — n/a

## Plano de testes (TDD)

### Unitários — back

| Caso | Arquivo teste | Status |
|------|---------------|--------|
| Gera request_id quando header ausente | `apps/api/internal/middleware/logging_test.go` | pending |
| Reutiliza X-Request-ID do cliente | `apps/api/internal/middleware/logging_test.go` | pending |
| Log contém campos obrigatórios | `apps/api/internal/middleware/logging_test.go` | pending |
| Handler health retorna status ok | `apps/api/internal/handler/health_test.go` | pending |

### Unitários — front

| Caso | Arquivo teste | Status |
|------|---------------|--------|
| n/a | — | n/a |

### Integração API

| Endpoint / fluxo | Cenários (sucesso + erros doc) | Arquivo teste | Status |
|------------------|--------------------------------|---------------|--------|
| GET /health | 200 + body OpenAPI + X-Request-ID | `apps/api/tests/integration/handler/health_test.go` | pending |
| GET /unknown | 404 + request_id no response | `apps/api/tests/integration/handler/not_found_test.go` | pending |

### E2E

| Fluxo | Persona | Passos | Resultado | Arquivo | Status |
|-------|---------|--------|-----------|---------|--------|
| n/a | — | — | — | — | n/a |

## Impactos

- API: `cmd/server`, middleware, handler health
- DB: n/a (health não consulta DB no MVP)
- Front: n/a
- Segurança: request_id não expõe PII
- Observabilidade: baseline para CARD-002+ e ingestão CARD-003

## Threat model

Não aplicável (`sensitive: false`).
