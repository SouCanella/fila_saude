---
name: feature-delivery
description: Delivers work from an active CARD using SDD and TDD. Use when implementing CARD-XXX, REQ spec within a card, or feature-delivery workflow.
---

# Feature delivery

## Prerequisites

- Workspace de **produto** (`.modelo-product-workspace` ou `template.is_upstream: false`) — entrega só na pasta irmã, não no Modelo upstream
- `bootstrap.status: complete`
- `mvp_planning.status: complete`
- **Card** `CARD-XXX` in `in_progress` covering the REQ(s) being implemented
- Spec exists with `status: approved` for each REQ in the card
- If UI: HTML mock exists; if new screen, design rules followed
- If `design.status != approved` and framework UI: stop — complete design approval first

## Checklist

0. Read card MD + confirm `card_ids` on each spec; use skill **card-tracking** if card not yet open
1. If new or large scope: run [req-validation-checklist.md](../../docs/specs/req-validation-checklist.md) §8
2. Read spec + DoR + **camadas de teste** marcadas + plano por camada (per REQ in card)
2b. `make quality-validate-specs` — plano coerente; `make quality-scaffold REQ=REQ-XXX` — stubs TDD red
3. Apply matrix in `docs/testing/tdd-workflow.md`
4. Update traceability matrix (in progress) for each REQ
5. **TDD order:** OpenAPI → unit back → integration/contract → unit front → E2E (if `critical_flow`)
6. Tests failing (red) → minimal code (green) → refactor — per layer
6b. Test names include `@req REQ-XXX` for CI export traceability
7. API: OpenAPI + error-catalog + integration/contract tests
8. E2E if `critical_flow: true` and `e2e.enabled`
9. Sync mock-api / HTML if per `docs/testing/contract-sync.md`
10. Security checklist; threat model if `sensitive: true`
11. Update `delivery-log.md` (CARD-XXX entry + REQs), matrix, specs
12. When **all** REQs in card meet DoD: close card via **card-tracking**
13. PR evidence: commands, coverage, risks
14. Each agent turn: skill **process-metrics** (round, context from active card); 3-line transparency summary
15. After tests: **quality-health** — `export-quality-run.sh` or `manual.yaml` + `make quality-build`
16. **Project Hub:** `make hub-build` após delivery-log, matrix ou specs — Overview reflete entregas e atividade
17. **Testes durante entrega:** se `agent_automation.run_tests_without_approval: true`, executar testes no escopo configurado sem pedir OK a cada comando; caso contrário, pedir antes. Commits continuam só quando o humano pedir — ver [commit-policy.md](../../docs/operations/commit-policy.md).

## Response format

- Card ID + REQs covered
- Files changed (prod + **tests**)
- Layers covered per REQ
- red/green evidence per layer
- Coverage %
- OpenAPI / HTML / DB impact
- Pending → `tech-debt.md`
