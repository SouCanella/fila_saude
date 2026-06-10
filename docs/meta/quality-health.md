# Saúde da qualidade (TDD + rastreio)

Painel separado do [tempo de processo](process-metrics.md) — foco em **cobertura de requisitos por camada de teste** e **última execução**. Acesse via **[Project Hub](project-hub/index.html)** (`make hub-serve`, aba `#quality`). Integração API e contrato OpenAPI são **uma camada** no painel.

## Ciclo fechado (spec → testes → painel)

```text
1. Spec approved — camadas [x] + plano TDD (tabelas por camada)
2. make quality-validate-specs     — coerência do plano
3. make quality-scaffold           — stubs TDD red (@req REQ-XXX nos testes)
4. feature-delivery — red → green por camada
5. export-quality-run.sh (CI) ou manual.yaml
6. make hub-build → Project Hub (#quality) + gaps
7. Fechar CARD quando gaps verdes ou tech-debt
```

## Comandos

```bash
make quality-validate-specs    # plano ↔ camadas marcadas
make quality-scaffold          # cria tests/ ausentes (REQ=REQ-001 opcional)
make quality-scaffold-dry      # preview
make hub-build
make hub-serve             # http://localhost:8090/project-hub/#quality
make hub-demo-serve        # demo :8091
```

Strict (exige coluna **Arquivo teste** em todas as linhas):

```bash
QUALITY_SPEC_STRICT=1 make quality-validate-specs
```

## Fonte da verdade

| Artefato | Papel |
|----------|--------|
| `docs/backlog/mvp-backlog.md` | REQs + `req_kind` |
| `docs/specs/REQ-*.md` | Camadas obrigatórias + plano TDD |
| `docs/traceability-matrix.md` | Rastreio manual |
| `docs/meta/quality-runs/latest.json` | Export CI (preferencial) |
| `docs/meta/quality-runs/manual.yaml` | Fallback manual |
| `docs/meta/quality-manifest.yaml` | Overrides file/scenario → REQ |
| `project.config.yaml` → `quality_health` | Paths e roots |

## Export CI e rastreio REQ

`export-quality-run.sh` enriquece `req_ids` via:

1. Tag `@req REQ-XXX` ou `REQ-XXX` no nome do teste JUnit
2. Mapa gerado das specs (coluna **Arquivo teste**)
3. Overrides em `quality-manifest.yaml`

## Demo

[examples/quality-health-demo](../../examples/quality-health-demo/README.md) — 5 REQs, 10 cenários E2E, gráficos executivos.

```bash
make quality-demo-serve   # :8093 — botão Executar testes
make quality-scaffold-demo  # stubs pendentes no demo
```

## NFR

Requisitos não funcionais usam o mesmo `REQ-XXX` com `req_kind: non_functional` no backlog e na spec.

## Skills

- **quality-health** — gaps, scaffold, export
- **feature-delivery** — TDD por camada a partir do plano na spec
