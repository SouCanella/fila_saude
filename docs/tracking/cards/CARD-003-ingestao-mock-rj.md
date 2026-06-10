---
id: CARD-003
phase: FASE-1
status: open
title: Ingestão mock RJ
req_ids: [REQ-004]
specs: []
external_id: null
external_url: null
assignee: null
branch: null
pr: null
opened_at: null
done_at: null
---

# CARD-003 — Ingestão mock RJ

## Objetivo

Adapter mock com 13 hospitais RJ (paridade `filasaude-mock.js`), job agendado, cache Redis e **rating simulado**.

## REQs vinculados

| REQ_ID | Spec | Status spec |
|--------|------|-------------|
| REQ-004 | docs/specs/REQ-004-ingestao-mock-rj.md | draft |

## Escopo ampliado (REQ-004) — rating simulado

| Campo | MVP | Evolução |
|-------|-----|----------|
| `rating` | `decimal(2,1)` estático no seed (paridade mock JS) | Google Places FASE-4+ |
| `reviews_count` | inteiro simulado | Places API |
| `google_place_id` | **null** no MVP | opcional futuro |

**Regra:** UI exibe “Google simulado” ou “Avaliação pública (simulada)” — **não** chamar Places no MVP.

Inclui: especialidades, filas Manchester, `source_name`, `captured_at`, adapter pattern (`internal/adapters/mock_rj`).

## Critério de conclusão do card

- [ ] Spec REQ-004 approved
- [ ] Seed 13 hospitais + snapshots; job 5 min
- [ ] API lista/detail retorna `rating` + frescor; cache invalidado pós-ingestão

## Notas

Depende de CARD-002. Fecha FASE-1. Mock JS: `design-references/shared/filasaude-mock.js`.
