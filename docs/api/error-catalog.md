# Catálogo de erros da API

Formato padrão de resposta de erro:

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Mensagem legível",
  "details": {},
  "traceId": "uuid-opcional"
}
```

## Tabela

| HTTP | code | Quando usar | Exemplo message |
|------|------|-------------|-----------------|
| 400 | VALIDATION_ERROR | Payload inválido | Campo X obrigatório |
| 401 | UNAUTHORIZED | Sem auth | Token ausente |
| 403 | FORBIDDEN | Sem permissão | Acesso negado |
| 404 | NOT_FOUND | Recurso inexistente | Item não encontrado |
| 409 | CONFLICT | Conflito de estado | Registro duplicado |
| 500 | INTERNAL_ERROR | Erro técnico | Erro interno |

Testes de integração devem assertar `code` e estrutura para **cada** erro documentado na OpenAPI.
