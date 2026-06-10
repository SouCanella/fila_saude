# Discovery questionnaire (fase 0 — leve)

One topic per turn. Finalize on human confirmation of [vision-review.md](../../docs/discovery/vision-review.md).

## Topics

| # | Topic | Questions (examples) |
|---|--------|----------------------|
| 1 | Problema e objetivo | What problem? Success in 6–12 months? |
| 2 | Usuários e escala | Who uses it? Expected users/concurrency? |
| 3 | Experiência | Web, mobile, both? Mobile-first? Offline? |
| 4 | Restrições | LGPD, payments, integrations, deadline, team size |
| 5 | MVP (narrativo) | Minimum viable scope; explicit out-of-scope |
| 6 | Stack (suggestions) | Preferences; propose back/front/DB/CI with rationale → `bootstrap-hints.md` |

**Fases, REQs e cards:** fase 2 — skill **project-mvp-planning** (após bootstrap + mocks aprovados).

## Generated files (fase 0)

| File | Content |
|------|---------|
| `docs/discovery/product-discovery.md` | Conversation synthesis |
| `docs/discovery/bootstrap-hints.md` | Draft hints for bootstrap B–N |
| `docs/discovery/vision-review.md` | Human checklist |
| `docs/01-product-vision.md` | Optional draft |

## Config on complete

```yaml
discovery:
  status: complete
  completed_at: <ISO>
  review_confirmed_at: <ISO>  # vision-review confirmado
```
