---
id: CARD-009
phase: FASE-3
status: open
title: Admin integrações
req_ids: [REQ-013]
specs: []
external_id: null
external_url: null
assignee: null
branch: null
pr: null
opened_at: null
done_at: null
---

# CARD-009 — Admin integrações

## Objetivo

Painel admin: **login**, status de fontes (defasagem, SLA, cobertura), API protegida JWT.

## REQs vinculados

| REQ_ID | Spec | Status spec |
|--------|------|-------------|
| REQ-013 | docs/specs/REQ-013-admin-integracoes.md | draft |

## Escopo ampliado (REQ-013)

**Backend**

- `POST /api/v1/admin/login` (ou session) — credenciais via env no MVP piloto
- `GET /api/v1/integrations/status` — Bearer JWT; 401/403 documentados
- RBAC mínimo: `admin` (write/read), `viewer` (read-only)

**Frontend**

- Tela login admin (simples — email/senha ou token único MVP)
- `admin-status.html` replicada após auth
- Redirect se não autenticado

**Fora do MVP:** SSO, recuperação de senha, multi-tenant.

## Critério de conclusão do card

- [ ] Spec REQ-013 approved
- [ ] Fluxo login → painel; API status com JWT
- [ ] Testes integração 401/403 + login happy path

## Notas

Mockup: `design-references/screens/admin-status.html`. Depende CARD-003 (dados integração).
