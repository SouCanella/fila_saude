---
id: REQ-002
title: Schema e migrations
status: approved
approved_at: "2026-06-10T04:30:00Z"
approved_by: Romulo Canella
req_kind: functional
critical_flow: false
sensitive: false
card_ids: [CARD-001]
openapi_operations: []
mock_screens: []
visual_reference: null
---

# REQ-002 — Schema e migrations

## Objetivo

Definir e versionar o schema PostgreSQL/PostGIS para hospitais, especialidades e snapshots de fila, permitindo persistência geo e ingestão posterior (CARD-003).

## Escopo incluído

- Migrations (goose ou atlas) em `apps/api/migrations/`
- Tabelas MVP FASE-1:
  - `hospital` — id, name, address, location (GEOGRAPHY/POINT PostGIS), rating, reviews_count, google_place_id (nullable), uf, active, created_at, updated_at
  - `specialty` — id, slug, name
  - `queue_snapshot` — id, hospital_id, specialty_id, risk_level (Manchester), waiting_count, avg_wait_minutes_24h, avg_wait_minutes_7d, source_name, captured_at
- Índices: GIST em `hospital.location`; FKs hospital_id / specialty_id
- Tabelas preparatórias (schema only, sem lógica): `data_source`, `integration_health` (campos conforme arquitetura)
- Seed vazio ou fixture mínima para testes (1 hospital) — seed completo RJ fica REQ-004

## Escopo fora

- API REST de consulta (REQ-003)
- Job de ingestão e adapter mock (REQ-004)
- Migrations de auth admin (REQ-013)

## Regras de negócio

- `risk_level` enum: vermelho, laranja, amarelo, verde, azul (Manchester)
- `captured_at` obrigatório em `queue_snapshot`; histórico por insert (não overwrite silencioso na ingestão — ingestão define política em REQ-004)
- `google_place_id` nullable no MVP (rating simulado)
- Coordenadas WGS84 (SRID 4326)

## Critérios de aceite

- [ ] `goose up` (ou equivalente) aplica todas migrations em DB limpo
- [ ] `goose down` reverte última migration sem erro
- [ ] Consulta geo `ST_DWithin` funciona em teste de integração
- [ ] Repositório/domain consegue persistir e ler hospital + snapshot mínimo

## Cenários de sucesso

1. Migration up cria tabelas com constraints e índices
2. Insert hospital com POINT(-22.9, -43.2) retorna distância correta em query de proximidade

## Cenários de erro

1. Insert snapshot sem hospital_id → FK violation
2. risk_level inválido → constraint check falha
3. Migration down com dados dependentes → erro documentado ou CASCADE explícito na spec de migration

## DoR checklist

- [x] Objetivo claro
- [x] Aceite testável
- [x] Cenários erro definidos
- [x] Impacto técnico estimado
- [x] Estratégia de teste
- [x] `critical_flow: false`
- [x] Dependências: REQ-001 (Postgres compose)
- [ ] HTML mock (n/a)
- [ ] OpenAPI (n/a — sem endpoint)

## Camadas de teste

- [x] Unitário back (domain, validações, repos mock)
- [ ] Unitário front — n/a
- [x] Integração (migrations + PostGIS + repository)
- [ ] E2E — n/a

## Plano de testes (TDD)

### Unitários — back

| Caso | Arquivo teste | Status |
|------|---------------|--------|
| Validar risk_level Manchester permitidos | `apps/api/internal/domain/queue_snapshot_test.go` | pending |
| Hospital active default true | `apps/api/internal/domain/hospital_test.go` | pending |
| Repository insert/find hospital (sqlmock ou interface) | `apps/api/internal/repository/hospital_test.go` | pending |

### Unitários — front

| Caso | Arquivo teste | Status |
|------|---------------|--------|
| n/a | — | n/a |

### Integração (DB + migrations)

| Endpoint / fluxo | Cenários (sucesso + erros doc) | Arquivo teste | Status |
|------------------|--------------------------------|---------------|--------|
| Migrations up/down | Schema completo após up; tabelas removidas após down controlado | `apps/api/tests/integration/migrations/migrations_test.go` | pending |
| PostGIS ST_DWithin | Hospital dentro de raio 25 km | `apps/api/tests/integration/repository/hospital_geo_test.go` | pending |
| FK queue_snapshot | Insert órfão falha | `apps/api/tests/integration/repository/snapshot_test.go` | pending |
| Persistência round-trip | Insert hospital + snapshot + read | `apps/api/tests/integration/repository/hospital_repo_test.go` | pending |

### E2E

| Fluxo | Persona | Passos | Resultado | Arquivo | Status |
|-------|---------|--------|-----------|---------|--------|
| n/a | — | — | — | — | n/a |

## Impactos

- API: camada repository pronta para handlers (CARD-002)
- DB: schema versionado; ver `docs/02-architecture.md`
- Front: n/a
- Segurança: sem PII neste schema base
- Observabilidade: n/a

## Threat model

Não aplicável (`sensitive: false`).
