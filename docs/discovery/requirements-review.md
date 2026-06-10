# Revisão de requisitos (IA) — FilaSaúde Brasil

_Data da revisão: 2026-06-10 (rev. auditoria + melhorias aplicadas)_  
_Revisor IA + confirmação humana: **aprovado** — 2026-06-10_

## Status geral

- [x] **ok** — backlog, fases e cards coerentes; lacunas da auditoria endereçadas
- [ ] **gaps** — lacunas aceitas/adiadas pelo humano
- [ ] **blocking** — resolver antes de `mvp_planning.status: complete`

---

## Melhorias aplicadas (2026-06-10)

| Item | Ação | Onde |
|------|------|------|
| OSRM no compose | REQ-001 ampliado (PostGIS + Redis + **OSRM**) | `mvp-backlog.md`, CARD-001, CARD-007 |
| Segurança API pública | Rate limit, CORS, security headers em REQ-003 | `mvp-backlog.md`, CARD-002 |
| `GET /hospitals/{id}` | Explícito em REQ-003 e DoD CARD-002 | backlog + card |
| Rating simulado | Seed estático em REQ-004; exibição REQ-008; **sem Google Places** | `mvp-backlog.md`, CARD-003 |
| Login admin | Fluxo UI + JWT em REQ-013 | `mvp-backlog.md`, CARD-009 |
| CARD-005 oversized | **Manter 10 cards** — DoD por tela; PRs internos se >400 linhas | CARD-005, § Decisão abaixo |

---

## Decisão: 10 cards (CARD-005 não splitado)

| Opção | Prós | Contras | Decisão |
|-------|------|---------|---------|
| **Manter 10 cards** | Menos overhead de tracking; jornada cidadão coesa; alinhado a 3 fases | CARD-005 grande (4 telas, 2 critical_flows) | **Adotado** |
| Split CARD-005 → 11 | PRs menores | +1 card, fase 2 desbalanceada, REQ-006/007 acoplados | Rejeitado no MVP |

**Mitigação:** CARD-005 documenta DoD por mock (`index`, `onboarding`, `mapa`, `lista`); entrega incremental por PR mantendo um único card.

---

## Auditoria de rastreabilidade

| REQ_ID | Objetivo | Em mvp-backlog | Em traceability-matrix | Card | Status |
|--------|----------|----------------|------------------------|------|--------|
| REQ-001 | O3 | sim | sim | CARD-001 | ok (OSRM) |
| REQ-002 | O2 | sim | sim | CARD-001 | ok |
| REQ-003 | O1, O2 | sim | sim | CARD-002 | ok (+ segurança) |
| REQ-004 | O2, O3 | sim | sim | CARD-003 | ok (+ rating simulado) |
| REQ-005 | O4 | sim | sim | CARD-004 | ok |
| REQ-006 | O1, O4 | sim | sim | CARD-005 | ok |
| REQ-007 | O1 | sim | sim | CARD-005 | ok |
| REQ-008 | O1, O2 | sim | sim | CARD-006 | ok |
| REQ-009 | O1 | sim | sim | CARD-006 | ok |
| REQ-010 | O1 | sim | sim | CARD-007 | ok (dep. OSRM CARD-001) |
| REQ-011 | O1 | sim | sim | CARD-008 | ok |
| REQ-012 | O1 | sim | sim | CARD-008 | ok |
| REQ-013 | O2 | sim | sim | CARD-009 | ok (+ login admin) |
| REQ-014 | O2 | sim | sim | CARD-001 | ok |
| REQ-015 | O1 | sim | sim | CARD-010 | ok |

### Objetivos sem REQ

| Objetivo | Ação |
|----------|------|
| — | nenhum — O1–O4 cobertos |

### REQs órfãos (sem objetivo)

| REQ_ID | Ação |
|--------|------|
| — | nenhum |

### REQs sem card

| REQ_ID | Card proposto | Ação |
|--------|---------------|------|
| — | — | todos vinculados |

---

## Fases e cards

### Fases

| Fase | Objetivo | Cards | ok / gap |
|------|----------|-------|----------|
| FASE-1 | Fundação + dados RJ | CARD-001, CARD-002, CARD-003 | ok |
| FASE-2 | UX cidadão | CARD-004 … CARD-008 | ok |
| FASE-3 | Admin + E2E | CARD-009, CARD-010 | ok |

### Cards

| CARD_ID | Fase | REQs | Tamanho | MD existe | ok / gap |
|---------|------|------|---------|-----------|----------|
| CARD-001 | FASE-1 | REQ-001, REQ-002, REQ-014 | ok | sim | ok |
| CARD-002 | FASE-1 | REQ-003 | ok | sim | ok |
| CARD-003 | FASE-1 | REQ-004 | ok | sim | ok |
| CARD-004 | FASE-2 | REQ-005 | ok | sim | ok |
| CARD-005 | FASE-2 | REQ-006, REQ-007 | **grande** (aceito) | sim | ok — não split |
| CARD-006 | FASE-2 | REQ-008, REQ-009 | ok | sim | ok |
| CARD-007 | FASE-2 | REQ-010 | ok | sim | ok |
| CARD-008 | FASE-2 | REQ-011, REQ-012 | ok | sim | ok |
| CARD-009 | FASE-3 | REQ-013 | ok | sim | ok |
| CARD-010 | FASE-3 | REQ-015 | ok | sim | ok |

**Total: 10 cards, 15 REQs, 3 fases.**

---

## Lacunas encontradas

| Item | Severidade | Cobertura | Ação |
|------|------------|-----------|------|
| Login usuário final | — | fora MVP | discovery §8 |
| Push notifications | média | fora MVP | REQ-011 localStorage only |
| Google Maps / Places / rating real | média | adiado FASE-4+ | **rating simulado** REQ-004/008 |
| Integração real DF/municipal | alta | adiado FASE-4+ | REQ-004 mock primeiro |
| PWA / offline | baixa | fora MVP | — |
| i18n | baixa | fora MVP | pt-BR only |
| Pagamento | — | fora MVP | — |
| Observabilidade | média | REQ-014 | CARD-001 |
| LGPD | crítica | REQ-012 | copy + consent geo |
| Rate limit / CORS | média | **REQ-003** | resolvido na auditoria |
| OSRM infra | média | **REQ-001** | resolvido na auditoria |
| Admin login UI | média | **REQ-013** | resolvido na auditoria |

---

## Propostas da IA

| Proposta | Tipo | Decisão |
|----------|------|---------|
| REQ-014 observabilidade no CARD-001 | agrupamento | aceito |
| REQ-011 alertas só localStorage | escopo MVP | aceito |
| 3 fases / **10 cards** / 15 REQs | fatiamento | **aceito — CARD-005 único** |
| Ampliar REQ-001/003/013 + rating REQ-004 | escopo | aplicado no backlog |

---

## Coerência stack (bootstrap confirmado)

| Critério | ok / gap | Nota |
|----------|----------|------|
| Go + Next.js | ok | CARD-001, CARD-004 |
| PostGIS + Redis + OSRM | ok | CARD-001, CARD-003, CARD-007 |
| OSM + OSRM (não Google) | ok | REQ-010; rating simulado |
| VM + Docker deploy | ok | REQ-001 |
| LGPD geo consent | ok | REQ-006, REQ-012 |
| Segurança API baseline | ok | REQ-003 |

---

## Fatiamento

| REQ_ID | Tamanho | Dependências | Nota |
|--------|---------|--------------|------|
| REQ-001–004 | ok | sequencial FASE-1 | OSRM + mock + API segura |
| REQ-005–010 | ok | REQ-003, REQ-001 (010) | front após API |
| REQ-013 | ok | REQ-004 | admin após dados |
| REQ-015 | ok | REQ-010 | E2E por último |

---

## Confirmação humana

- [x] Li o relatório e **aprovo** o planejamento MVP (fases, REQs, cards)
- [ ] Ajustes solicitados: _(nenhum)_
- Responsável: Romulo Canella
- Data: 2026-06-10

_Gate fechado: `mvp_planning.status: complete` em `project.config.yaml`._
