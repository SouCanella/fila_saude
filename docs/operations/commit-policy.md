# Política de commits

> Gerado/atualizado no bootstrap bloco **O — Entrega**. Valores canônicos em `project.config.yaml` → `git.commit`.

## Convenção

| Campo | Valor |
|-------|-------|
| Formato | `conventional` |
| Escopo obrigatório | não |
| Referência CARD/REQ | footer |
| Quem commita | humano ou agente (agente só quando pedido ou policy permitir) |

## Formato (Conventional Commits)

```
tipo(escopo opcional): descrição curta

Corpo opcional.

CARD-XXX · REQ-YYY
```

### Tipos comuns

| Tipo | Uso |
|------|-----|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Documentação |
| `test` | Testes |
| `chore` | Manutenção, deps, CI |

### Exemplos

```
feat(auth): login com JWT

CARD-001 · REQ-001
```

```
fix(checkout): corrige total com desconto

CARD-003 · REQ-004
```

## Hooks

Ver [`templates/hooks/README.md`](../../templates/hooks/README.md) — lint/test antes do commit quando configurado no bootstrap.

## Regras para agentes de IA

- Seguir esta policy; não inventar formato divergente.
- **Commit** continua só quando o humano pedir (user rule) — policy não autoriza push automático.
