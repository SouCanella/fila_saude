---
id: CARD-005
phase: FASE-2
status: open
title: Onboarding, mapa e lista
req_ids: [REQ-006, REQ-007]
specs: []
external_id: null
external_url: null
assignee: null
branch: null
pr: null
opened_at: null
done_at: null
---

# CARD-005 — Onboarding, mapa, lista e início

## Objetivo

Jornada principal cidadão: landing, onboarding geo, mapa MapLibre, lista ranking — consumindo API v1.

> **Decisão:** card **único** (não splitado) — 4 telas, 2 REQs; entrega incremental por PR interno se necessário.

## REQs vinculados

| REQ_ID | Spec | Status spec |
|--------|------|-------------|
| REQ-006 | docs/specs/REQ-006-onboarding-geo.md | draft |
| REQ-007 | docs/specs/REQ-007-mapa-lista.md | draft |

## Paridade mock (por tela)

| Mock | REQ | DoD resumido |
|------|-----|--------------|
| `index.html` | REQ-007 | Landing SSR, KPIs, top 3 hospitais, links mapa/lista |
| `onboarding.html` | REQ-006 | Geo consent, endereço manual, especialidade, aviso SAMU |
| `mapa.html` | REQ-007 | MapLibre, filtros, marcadores, modal, estados `?state=` |
| `lista.html` | REQ-007 | Cards ranking, filtros, favoritar |

## Critério de conclusão do card

- [ ] Specs approved
- [ ] 4 telas com paridade visual + TanStack Query
- [ ] critical_flow: `onboarding_to_map`, `map_to_hospital_detail`
- [ ] Estados loading/erro/vazio replicados do mock

## Camadas TDD

| REQ | unit front | integração | E2E |
|-----|------------|------------|-----|
| REQ-006 | forms, consent | API geo params | onboarding_to_map |
| REQ-007 | filtros, ranking | API hospitals list | map_to_hospital_detail |

## Notas

Card grande — se PR > 400 linhas, subdividir commits por tela mantendo um card. Depende CARD-004.
