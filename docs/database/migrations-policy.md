# Política de migrations

- Toda alteração de schema: migration versionada
- Rollback documentado
- Impacto em dados existentes e índices
- Testes de integração com massa representativa
- **Proibido** alterar DB em prod sem migration

Bootstrap bloco C: se `has_database: true`, configurar ferramenta de migration na stack.
