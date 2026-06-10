# Política de versionamento de API — FilaSaúde Brasil

Definido no bootstrap (bloco F — 2026-06-09).

## Estratégia

- **URL path:** `/api/v1/` — breaking changes incrementam major (`/api/v2/`)
- **OpenAPI:** `info.version` segue SemVer da API (independente do produto)
- **Versão inicial API:** `0.1.0`

## Depreciação

1. Marcar endpoint como `deprecated: true` na OpenAPI
2. Header de resposta `Deprecation: true` + `Sunset: <RFC 7231 date>`
3. Prazo mínimo: **90 dias** antes de remover
4. Documentar em CHANGELOG e `delivery-log.md`

## Breaking change

- **ADR obrigatório** antes de remover ou alterar contrato publicado
- Testes de compatibilidade retroativa quando clientes externos existirem

## SemVer da API

| Incremento | Quando |
|------------|--------|
| MAJOR (v1 → v2) | Remoção/alteração incompatível de campos ou paths |
| MINOR | Novos endpoints ou campos opcionais |
| PATCH | Correções de documentação ou comportamento bugfix compatível |

Documentar versão atual em OpenAPI `info.version`.

## Referências

- Contrato: [openapi.yaml](openapi.yaml)
- Erros: [error-catalog.md](error-catalog.md)
