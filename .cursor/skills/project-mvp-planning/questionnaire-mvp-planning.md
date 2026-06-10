# MVP planning questionnaire (fase 2)

After bootstrap + design approved (if front). One topic per turn.

## Topics

| # | Topic | Questions (examples) |
|---|--------|----------------------|
| 1 | **Fases** | FASE-1 MVP, FASE-2… objectives and done criteria |
| 2 | **REQs** | REQ-001… per phase ([req-slicing.md](../../docs/specs/req-slicing.md)) |
| 3 | **Cards** | CARD-001… group REQs; create MD files |
| 4 | **IA review** | Checklist → `requirements-review.md` → human confirms |

## Generated files

| File | Content |
|------|---------|
| `docs/planning/mvp-phases.md` | Fases FASE-1… |
| `docs/planning/cards-backlog.md` | Index CARD → fase → REQs |
| `docs/tracking/cards/CARD-XXX-*.md` | One MD per card |
| `docs/backlog/mvp-backlog.md` | REQ backlog |
| `docs/discovery/requirements-review.md` | IA validation + human decisions |
| `docs/traceability-matrix.md` | Rows per REQ, status `backlog` |

## Config on complete

```yaml
mvp_planning:
  status: complete
  completed_at: <ISO>
  review_confirmed_at: <ISO>
```

## Traceability rules

- Every REQ → ≥1 card + matrix row.
- Every card → file in `docs/tracking/cards/`.
- Run `./scripts/validate-planning.sh` before marking complete.
