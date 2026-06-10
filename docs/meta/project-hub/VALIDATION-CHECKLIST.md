# Validação Hub — PoC ready

Checklist humano complementar a `scripts/validate-hub-complete.sh`.

## Comandos gate

```bash
make ci
make hub-validate-complete
make hub-demo-serve   # smoke manual Overview
python3 scripts/resolve_next_step.py --root . --json
./scripts/test_spawn_e2e.sh   # spawn pasta irmã (também no CI)
```

## PoC hardening (CARD-Hub-PoC-Ready)

- [x] IDs slug centralizados (`scripts/modelo_ids.py`) — delivery, journey, quality, next_step
- [x] Template: delivery mostra `CARD-Hub-Evolucao` no Overview
- [x] Template: KPI OpenAPI **stub/pendente** (`openapi_valid: false`)
- [x] Demo: KPI OpenAPI **valid** (`openapi_valid: true`)
- [x] CI GitHub espelha `make ci` (hub steps + `HUB_JSON_STRICT=all` + `RETRO_STRICT=1`)
- [x] `check-hub-embeds.sh` anti-drift integrado em hub-validate
- [x] `sync-card-github.sh --dry-run` + `external_url` no `open`
- [x] Compliance hint bootstrap (blocos I/N) no Overview
- [x] Cards meta indexados em `cards-backlog.md` (seção Meta)
- [x] Demo PoC único — [demo-matrix.md](demo-matrix.md)

## E2E Playwright — adiado

- Playwright **não roda em CI** nesta rodada.
- Opcional manual: `make hub-e2e-demo` (requer browsers instalados).
- Arquivos mantidos em `tests/e2e/hub/` para uso futuro.

## Wave 1–3 (Hub Evolução — referência)

Itens da entrega anterior CARD-Hub-Evolucao; validados via `hub-validate-complete`:

- Funil, entregas expansíveis, retro por fase, tech-debt/OpenAPI/compliance/release KPIs
- Embeds unificados, sync-card-github documentado, discovery checklist no funil

## Gate final

- [x] `make ci` verde
- [x] `delivery-log.md` + `traceability-matrix.md` com REQ-Hub-PoC-Ready
- [x] CARD-Hub-PoC-Ready fechado
