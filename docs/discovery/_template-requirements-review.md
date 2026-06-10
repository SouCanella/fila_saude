# Revisão de requisitos (IA)

_Data da revisão: YYYY-MM-DD_  
_Revisor IA + confirmação humana:_

## Status geral

- [ ] **ok** — pode concluir descoberta
- [ ] **gaps** — lacunas aceitas/adiadas pelo humano
- [ ] **blocking** — resolver antes de `discovery.status: complete`

## Auditoria de rastreabilidade

| REQ_ID | Objetivo (O#) | Em mvp-backlog | Em traceability-matrix | Status |
|--------|---------------|----------------|------------------------|--------|
| REQ-001 | O1 | sim | sim | ok |

### Objetivos sem REQ

| Objetivo | Ação |
|----------|------|
| | criar REQ / fora do MVP |

### REQs órfãos (sem objetivo)

| REQ_ID | Ação |
|--------|------|
| | vincular / remover |

### REQs sem card

| REQ_ID | Card proposto | Ação |
|--------|---------------|------|
| | CARD-00X | vincular |

## Fases e cards

### Fases

| Fase | Objetivo | Cards | ok / gap |
|------|----------|-------|----------|
| FASE-1 | | CARD-001, CARD-002 | |

### Cards

| CARD_ID | Fase | REQs | Tamanho | MD existe | ok / gap |
|---------|------|------|---------|-----------|----------|
| CARD-001 | FASE-1 | REQ-001, REQ-002 | ok / grande | sim | |

### Fase sem cards

| Fase | Ação |
|------|------|
| | criar cards |

## Lacunas encontradas

| Item | Severidade | Cobertura | Ação |
|------|------------|-----------|------|
| Auth / login | crítica | ausente | REQ-00X |
| Erros / empty states | média | parcial | ampliar REQ-00Y |
| LGPD | crítica | ausente | REQ ou fora MVP |
| Admin | baixa | fora MVP | adiar |
| Notificações | média | ausente | propor REQ |
| Observabilidade | média | bootstrap G | — |
| i18n | baixa | fora MVP | — |
| Pagamento | crítica | ausente | REQ |
| Integrações externas | média | | |

## Propostas da IA (não pensadas ainda)

| Proposta | Tipo | Decisão humana |
|----------|------|----------------|
| REQ-00X — … | novo REQ | aceito / rejeitado / adiado |

## Coerência stack (bootstrap-hints)

| Critério | ok / gap | Nota |
|----------|----------|------|
| Escala vs stack | | |
| Mobile-first vs front | | |
| LGPD vs sensitive flows | | |

## Fatiamento (req-slicing)

| REQ_ID | Tamanho | Dependências | Nota |
|--------|---------|--------------|------|
| REQ-001 | ok / grande | | |

## Ações antes do bootstrap

1.
2.

## Confirmação humana

- [ ] Li o relatório e aceito concluir a descoberta (com gaps adiados documentados acima)
- Responsável:
- Data:
