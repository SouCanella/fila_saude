# Cards — abrir, atualizar, fechar

Cards são **obrigatórios**. O Markdown em `docs/tracking/cards/` é sempre a fonte de verdade no git (`mirror_in_repo: true`).

## Hierarquia

**Fase** → **Card** (unidade de trabalho) → **REQ** (contrato/spec/TDD)

Desenvolvimento parte do **card**, não diretamente do REQ.

## Provider (`tracking.cards.provider`)

| Provider | Uso |
|----------|-----|
| `markdown` | Só MD no repo (padrão) |
| `github_issues` | `gh issue create/edit/close` + espelho MD |
| `jira` | API + `.env` (`JIRA_*`) + espelho MD |
| `kanbanize` | API + `.env` (`KANBANIZE_*`) + espelho MD |
| `azure_devops` | API + `.env` (`AZURE_DEVOPS_*`) + espelho MD |

Configurado no bootstrap bloco **J** (2026-06-09). Provider: **markdown** — cards e REQs serão criados na fase **project-mvp-planning**.

## Projeto FilaSaúde Brasil

## Ciclo de vida

| Ação | Card status | Quando |
|------|-------------|--------|
| **Abrir** | `in_progress` | Dev inicia trabalho; branch `feature/CARD-XXX-slug` |
| **Atualizar** | — | Link PR, notas, sync externo |
| **Fechar** | `done` | Todos REQs linkados com DoD + specs approved |

## Abrir card

1. Card em `open` no [cards-backlog.md](../planning/cards-backlog.md)
2. Todas specs dos `req_ids` com `status: approved` (ou aprovar antes)
3. Atualizar frontmatter `status: in_progress`, `branch`
4. Se provider externo: criar issue e preencher `external_id` / `external_url`

## GitHub Issues (exemplo)

```bash
gh issue create --title "[CARD-001] Autenticação MVP" \
  --body "REQs: REQ-001, REQ-002" --label "card"
```

Atualizar `external_url` no arquivo MD do card.

Script auxiliar (dry-run sem rede):

```bash
./scripts/sync-card-github.sh open CARD-001 --dry-run
./scripts/sync-card-github.sh close CARD-001 --dry-run
./scripts/sync-card-github.sh comment CARD-001 --body "Atualização" --dry-run
```

Requer `gh auth login` quando não usar `--dry-run`.

## Fechar card

1. DoD de **cada** REQ linkado
2. `delivery-log.md` referencia CARD-XXX
3. Card `status: done`; matrix atualizada
4. Fechar issue externa se existir

## Gates

- Sem card `in_progress`: **proibido** feature-delivery
- REQ no backlog sem card: **proibido** concluir descoberta
- Card pode referenciar **N REQs**; PR preferencialmente por card

Skill: `card-tracking` | Rule: `015-card-tracking.mdc`
