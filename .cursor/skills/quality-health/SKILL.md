---
name: quality-health
description: Build and interpret quality health dashboard — REQ test coverage, last run pass/fail, gaps. Use after TDD, CI, or closing cards. Guides scaffold and gap-driven test creation.
---

# Quality health

## When

- After running test suite locally or CI
- Before/after closing CARD (camadas da spec)
- Human asks for gaps / uncovered REQs
- **Starting TDD** on a REQ — scaffold from spec plan

## Closed loop (spec → testes → painel)

```
spec approved (plano TDD)
  → make quality-validate-specs
  → make quality-scaffold REQ=REQ-XXX   # ou: make quality-scaffold -- --req REQ-XXX
  → TDD red → green (feature-delivery)
  → export-quality-run.sh / manual.yaml
  → make quality-build
  → painel: gaps ↓
```

## Steps

### 1. Validar plano na spec

```bash
make quality-validate-specs          # camadas [x] ↔ tabelas
QUALITY_SPEC_STRICT=1 make quality-validate-specs   # exige Arquivo teste
```

### 2. Scaffold (stubs TDD red)

```bash
make quality-scaffold                # cria arquivos ausentes do plano
make quality-scaffold REQ=REQ-001    # um REQ
make quality-scaffold-dry            # preview
```

Incluir `@req REQ-XXX` no nome do teste (JUnit/export enriquece req_ids).

### 3. Implementar gaps (por prioridade)

1. `make quality-build && make quality-serve`
2. Aba **Riscos e gaps** ou JSON `gaps[]`
3. Para cada gap: abrir `docs/specs/REQ-*.md` → linha da camada → TDD red→green
4. Atualizar coluna **Status** na spec (`done` quando arquivo criado)

### 4. Registrar execução

```bash
./scripts/export-quality-run.sh --junit-unit-back … --coverage-backend …
# ou editar docs/meta/quality-runs/manual.yaml
make quality-build
```

### 5. Fechar CARD

Gaps verdes ou entrada em `docs/tech-debt.md` (rule 082).

## Manual YAML (sem CI)

Update `tests[]` with `layer`, `req_ids`, `file`, `scenario`, `status: pass|fail|missing`.

## Response (3 lines)

1. Last run overall + source (ci_json / manual_yaml)
2. Gap count + top REQ IDs + próximo scaffold/linha spec
3. Command: `make quality-scaffold` / `make quality-serve`
