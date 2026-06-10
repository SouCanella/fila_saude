# Política de releases

> Gerado/atualizado no bootstrap bloco **O — Entrega**. Valores canônicos em `project.config.yaml` → `git.release`.

## Estratégia do produto

| Campo | Valor |
|-------|-------|
| Estratégia | SemVer MVP (`semver_mvp`) |
| Versão inicial | `0.1.0` |
| Prefixo de tag | `v` |
| CHANGELOG | `CHANGELOG.md` |
| Automação CI | manual |

## SemVer (resumo)

- **MAJOR** — breaking change (ADR obrigatório)
- **MINOR** — funcionalidade compatível
- **PATCH** — correção compatível

Tags Git: `v0.1.0`, `v0.2.0`, …

## Fluxo manual (padrão template)

1. Fechar cards da entrega / fase conforme governança
2. Atualizar `CHANGELOG.md` (seção `[Unreleased]` → nova versão)
3. Criar tag: `git tag v0.1.0`
4. Registrar release em `docs/delivery-log.md`

## Hotfix

Ver [hotfix.md](hotfix.md) — patch SemVer (`v0.1.1`) a partir de branch `hotfix/*`.

## API vs produto

Versionamento de **API OpenAPI** (`info.version`) é independente — ver [../api/versioning-policy.md](../api/versioning-policy.md) (bootstrap bloco F).

## Estratégias alternativas (bootstrap)

| Valor | Uso |
|-------|-----|
| `calver` | Tags por data (`v2026.06.0`) |
| `semver_mvp` | Tags + notas em delivery-log até MVP |
| `none` | Sem tags formais; só delivery-log |
