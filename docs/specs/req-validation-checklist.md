# Checklist — validação IA de requisitos

A IA executa este checklist e registra em [requirements-review.md](../discovery/requirements-review.md). Humano confirma antes de concluir descoberta ou aprovar spec ampla.

## 1. Cobertura do MVP

- [ ] Cada objetivo (O#) em `product-discovery` tem ≥1 REQ no backlog **ou** está marcado "fora do MVP"
- [ ] Nenhum REQ no backlog sem objetivo vinculado (órfão) — ou justificado

## 2. Lacunas típicas

Marcar: **coberto** | **ausente** | **fora do MVP** | **adiado**

| Área | Notas |
|------|-------|
| Autenticação / login | |
| Perfis / autorização | |
| Erros e empty states (UX) | |
| Admin / backoffice | |
| Notificações (email, push) | |
| LGPD / dados pessoais | |
| Observabilidade / logs | |
| Performance / escala | |
| Offline / PWA | |
| i18n | |
| Pagamento / billing | |
| Integrações externas | |
| Migração de dados | |

## 3. Não-funcionais

- [ ] Escala da conversa refletida em stack hints (cache, fila, DB…)
- [ ] Mobile-first refletido em front hints e telas MVP
- [ ] Segurança alinhada a dados sensíveis

## 4. Fatiamento ([req-slicing.md](req-slicing.md))

- [ ] Nenhum REQ descreve "projeto inteiro"
- [ ] REQ duplicados ou sobrepostos identificados
- [ ] Dependências entre REQ explícitas no backlog
- [ ] `critical_flow` só onde fluxo é realmente crítico

## 4b. Fases e cards (obrigatório)

- [ ] `mvp-phases.md` com FASE-1… e critérios de conclusão
- [ ] `cards-backlog.md` indexa todo CARD com fase e REQs
- [ ] **Todo REQ** no backlog referenciado em ≥1 card
- [ ] Arquivo MD em `docs/tracking/cards/` para cada CARD
- [ ] Nenhuma fase MVP sem pelo menos 1 card (ou justificado)
- [ ] Cards oversized flagados (muitos REQs / domínios misturados)

## 5. Rastreabilidade

- [ ] `REQ_ID` em `mvp-backlog` = linha em `traceability-matrix` (status coerente)
- [ ] Títulos alinhados entre backlog e matrix
- [ ] `01-product-vision` coerente com `product-discovery`

## 6. Stack (bootstrap-hints)

- [ ] Sugestão compatível com escala e restrições
- [ ] E2E sugerido só se `e2e.enabled` faria sentido no bootstrap L

## 7. Propostas novas

Listar itens **não mencionados** pelo humano com sugestão de REQ ou "fora do MVP".

## 8. Subconjunto — antes de aprovar spec REQ-XXX

Ao criar/atualizar uma spec (prompt Nova feature):

- [ ] DoR completo na spec
- [ ] Camadas de teste marcadas ([_template-feature-spec.md](_template-feature-spec.md))
- [ ] REQ existe no backlog ou matrix
- [ ] REQ vinculado a card em `card_ids` ou cards-backlog
- [ ] Dependências de outros REQ atendidas ou documentadas
- [ ] Impacto OpenAPI / HTML identificado

## Saída

Preencher [requirements-review.md](../discovery/_template-requirements-review.md) e pedir confirmação humana.
