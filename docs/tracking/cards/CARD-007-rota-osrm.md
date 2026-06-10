---
id: CARD-007
phase: FASE-2
status: open
title: Rota OSRM + MapLibre
req_ids: [REQ-010]
specs: []
external_id: null
external_url: null
assignee: null
branch: null
pr: null
opened_at: null
done_at: null
---

# CARD-007 — Rota OSRM + MapLibre

## Objetivo

Tela de rota com tempo/distância via **OSRM** (serviço do CARD-001); mapa OSM; passo a passo e avisos SAMU.

## REQs vinculados

| REQ_ID | Spec | Status spec |
|--------|------|-------------|
| REQ-010 | docs/specs/REQ-010-rota-osrm.md | draft |

## Dependências

- CARD-001 (OSRM no compose)
- CARD-006 (detalhe hospital)

## Critério de conclusão do card

- [ ] Spec REQ-010 approved
- [ ] `rota.html` replicada; rota calculada via OSRM local/staging
- [ ] Aviso emergência grave / SAMU visível
- [ ] critical_flow: `hospital_to_route`

## Notas

Mockup: `design-references/screens/rota.html`. Sem Google Directions no MVP.
