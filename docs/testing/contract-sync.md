# Sincronia OpenAPI ↔ mock ↔ HTML

## Ordem de mudança

| Tipo | Ordem |
|------|--------|
| API nova/alterada | OpenAPI → testes contrato (red) → `mock-api.js` → HTML se expõe dados |
| Só UI | HTML/mock → spec; OpenAPI se novo campo de API |

## Na spec

Preencher:

- `openapi_operations[]`
- `mock_screens[]`

## DoD

Endpoints usados na tela existem na OpenAPI e têm mock coerente em `design-references/shared/mock-api.js`.
