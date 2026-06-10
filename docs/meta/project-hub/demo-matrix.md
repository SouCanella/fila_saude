# Project Hub — matriz de demos

| Cenário | Comando | URL |
|---------|---------|-----|
| **PoC integrado** (recomendado, FilaSaúde + UI premium) | `make hub-demo-serve` | http://localhost:8091/project-hub/ |
| Template virgem (showcase) | `make hub-serve` | http://localhost:8090/project-hub/ |
| Legado process-metrics isolado | deprecated | — |
| Legado quality-health isolado | deprecated | — |

## PoC integrado

- Massa de dados em `examples/project-hub-demo/`; hub servido via symlinks para `docs/meta/project-hub` (`hub-serve-symlinks.sh`).
- `examples/project-hub-demo/project-hub/` é **gerado localmente** (gitignored) — não versionar cópias duplicadas.
- Entrypoint: [examples/project-hub-demo/README.md](../../examples/project-hub-demo/README.md).

## Validação

```bash
make hub-validate-complete
make ci
```

Checklist humano: [VALIDATION-CHECKLIST.md](VALIDATION-CHECKLIST.md).
