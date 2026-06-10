# Walkthrough — fluxo CRUD exemplo

Exemplo fictício para calibrar equipe e IA.

## 1. REQ-001 — Listar e criar itens

- Spec aprovada em `docs/specs/REQ-001-itens.md`
- `critical_flow: false`

## 2. HTML mock

- `design-references/screens/itens-lista.html`
- `design-references/screens/itens-form.html`
- Aprovado em `APPROVAL.md`

## 3. OpenAPI

```yaml
GET /v1/itens
POST /v1/itens
```

## 4. TDD back

Camadas: unit back + integração + contrato (endpoint na OpenAPI).

1. Teste integração GET /v1/itens — red
2. Implementação — green
3. Teste POST validação erro 400 — red → green

## 5. TDD front

Camadas: unit front (componente/hook).

1. Teste componente lista — red
2. Implementação fiel ao HTML — green

## 6. E2E

`critical_flow: false` neste exemplo — E2E **n/a**. Se fosse login ou pagamento: marcar `critical_flow: true` e incluir cenário E2E no plano da spec.

## 7. Entrega

- PR com checklist
- `delivery-log.md` + matrix atualizados
- Cobertura módulo >= 90%

## 8. CI

Pipeline verde: lint, unit, coverage, integração, OpenAPI validate.
