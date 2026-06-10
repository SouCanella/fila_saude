# Hotfix

## Quando usar

Correção urgente em produção.

## Processo

1. Branch `hotfix/*` (prefixo em `project.config.yaml`)
2. **TDD mínimo:** teste reproduz incidente → correção → green
3. Se violar gate (spec, design, cobertura): **ADR curto** obrigatório
4. PR com rollback documentado
5. Entrada no `delivery-log.md` em até **24h**
6. Tag de release conforme [release-policy.md](release-policy.md) (patch SemVer em hotfix)

## O que não pular

- Teste de regressão
- Segurança se tocar auth/dados sensíveis
- OpenAPI se alterar contrato
