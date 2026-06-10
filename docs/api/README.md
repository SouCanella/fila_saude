# API — contrato first

OpenAPI em `openapi.yaml` é o contrato oficial.

## Fluxo

1. Alterar OpenAPI
2. Testes de contrato/integração (red)
3. Implementação (green)
4. Atualizar error-catalog e mock-api se necessário

## Validação

Pipeline valida schema OpenAPI. Nenhum endpoint novo sem documentação.

Ver também: [error-catalog.md](error-catalog.md), [versioning-policy.md](versioning-policy.md).
