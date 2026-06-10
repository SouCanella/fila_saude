# Bootstrap questionnaire

Ask one block at a time. Update `project.config.yaml` after each.

**Prerequisite:** `discovery.status: complete` or `discovery.skipped: true`. If discovery complete, read `docs/discovery/*` and `docs/backlog/mvp-backlog.md` first — confirm hints in A/B instead of asking from zero.

## A — Identidade

- Nome do produto, domínio, responsáveis, idioma da documentação
- **Gera:** `docs/01-product-vision.md`

## B — Stack

- has_backend, has_frontend, has_database
- Linguagens, monorepo, ORM, auth
- **Gera:** `docs/02-architecture.md`, rules `02x-backend` / `03x-frontend` from templates if stack known

## C — Infra

- Docker, DB, filas, migrations tool
- **Gera:** architecture section, `templates/docker/` snippet if needed

## D — Testes

- Frameworks unit/integration, mutation yes/no
- **Gera:** `docs/testing/test-strategy.md`, coverage in config

## E — CI

- GitHub | GitLab | other
- **Gera:** copy `templates/ci/*.tpl` → `.github/workflows/` or `.gitlab-ci.yml`

## F — Contratos

- OpenAPI path, contract-first, versioning strategy, SLA defaults
- **Gera:** `docs/api/README.md`, versioning policy

## G — Observabilidade

- Log library, JSON format, correlation id, PII deny list
- **Gera:** `docs/observability/logging.md`, tune `060-logging.mdc`

## H — Design (if has_frontend)

- MVP features and screens list
- Co-create HTML per screen from `_template-screen.html`
- Set `mocks_complete: true` per screen
- **Gera:** `design-references/screens/*`, `docs/design-system.md`

## I — Segurança

- Rigor, secrets manager, SAST tools
- **Gera:** CI security gates

## J — Rastreio e cards (obrigatório)

- Confirm `card_prefix`, `phase_prefix`, `req_prefix`, branch naming
- **Cards:** always required; MD canonical in `docs/tracking/cards/`
- Refine cards from discovery; create missing CARD MD files if needed
- **Provider externo (opcional):** `markdown` (default) | `github_issues` | `jira` | `kanbanize` | `azure_devops`
- If external: `base_url`, `project_key`, `board_id`, `repo`; document in `.env.example`
- Optional first sync: create external issues mirroring cards MD
- **Gera:** [docs/operations/issue-cards.md](../../docs/operations/issue-cards.md), update `tracking.cards` in config, confirm specs template

## K — i18n

- Multilingual? If no: `i18n.enabled: false`, update `docs/i18n.md`

## L — E2E

- Tool, list critical flows (login, payment, etc.)
- `e2e.enabled`, `critical_flows[]` in config

## M — Ambientes

- dev/staging/prod vars
- **Gera:** `.env.example` from `templates/env/.env.example.tpl`, `docs/operations/environments.md`

## N — Privacidade

- LGPD applies? data categories, retention
- **Gera:** `docs/security/privacy-lgpd.md`

## O — Entrega (commits, releases, automação IA)

- **Commits:** convenção (`conventional` | `conventional_card` | `custom`), escopo obrigatório?, referência CARD no footer/scope?, quem commita (`human_only` | `human_or_agent`)
- **Releases:** estratégia (`semver` | `calver` | `semver_mvp` | `none`), versão inicial, prefixo tag, CHANGELOG path, automação CI (`manual` | `tag_on_main` | `github_release`)
- **Automação IA:** `run_tests_without_approval` (default `false`); escopo de testes (`unit_integration`, `e2e`, etc.); ambientes permitidos
- **Gera:** `docs/operations/commit-policy.md`, `docs/operations/release-policy.md`, stub `CHANGELOG.md` se semver; rule `085-agent-automation.mdc`

## Completion

All required sections `complete`. Required: A–G; H if frontend; I–O as applicable.

Set `bootstrap.status: complete`.
