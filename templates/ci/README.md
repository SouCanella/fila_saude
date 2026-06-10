# CI gates (obrigatórios)

Independente de plataforma (GitHub Actions, GitLab CI, etc.):

1. Install (clean)
2. Lint
3. Typecheck (se aplicável)
4. Unit tests — backend
5. Unit tests — frontend (se aplicável)
6. Coverage >= `{{COVERAGE_THRESHOLD}}` (back e front separados)
7. API integration tests — 100% documented endpoints
8. OpenAPI schema validate
9. Contract tests
10. SAST / dependency scan / secret scan
11. Build
12. E2E (se `e2e.enabled: true` — fluxos críticos)

Merge bloqueado se qualquer gate falhar.

## Templates

- `github-actions.yml.tpl` — substituir `{{COVERAGE_THRESHOLD}}`, `{{OPENAPI_PATH}}`
- `gitlab-ci.yml.tpl` — idem

Gerados no bootstrap bloco E.
