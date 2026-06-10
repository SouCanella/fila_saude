---
name: project-hub
description: Project Hub unificado — build, serve, overview, next_step. Use for hub-build, project-hub panel, or unified project visualization.
---

# Project Hub

## Comandos

```bash
make hub-build
make hub-serve           # :8090/project-hub/
make hub-demo-serve      # :8091
python3 scripts/resolve_next_step.py --root . --json
```

## UI premium

Shell SPA em `docs/meta/project-hub/`: `hub-premium.js` + `hub-data.js` + `premium.css`. Processo/Qualidade = legado montado em `#contentRoot` (sem iframe). Atualizar → `POST /api/refresh`.

## Módulos

Overview · Process · Quality · Security · A11y · Design (+ entregas e aprendizado no Overview)

JSON: **12 arquivos** em `docs/meta/project-hub/data/` — ver [project-hub.md](../../docs/meta/project-hub.md):

`hub`, `process`, `quality`, `security`, `a11y`, `design`, `delivery`, `learning`, `journey`, `tech_debt`, `openapi`, `release`.

Overview inclui funil de fases, entregas por CARD e feed de atividade (`journey.data.json`). No Modelo upstream com `upstream_dev_mode`, exibe **banner spawn** e `next_step` fase `spawn` (informativo). `hub.data.json` expõe `template.*` para o banner. KPI OpenAPI no template virgem mostra **stub/pendente** quando não há paths. CI: [ci-ritual.md](../../docs/meta/project-hub/ci-ritual.md). PoC demo: [demo-matrix.md](../../docs/meta/project-hub/demo-matrix.md).

## Após entrega

1. `make hub-build`
2. Responder com **## Próximo prompt sugerido** (rule 084) — mesmo conteúdo que `hub.data.json` → `next_step.prompt`

## Não confundir

- **Project Hub** = visão consolidada do projeto
- **process-metrics** / **quality-health** = módulos embutidos (embed); URLs antigas redirecionam
