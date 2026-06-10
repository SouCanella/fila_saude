---
id: REQ-001
title: Login e sessão
status: approved
req_kind: functional
critical_flow: true
sensitive: true
card_ids: [CARD-001]
---

# REQ-001 — Login e sessão (showcase Hub)

## Threat model

| Ameaça | Mitigação |
|--------|-----------|
| Brute force | Rate limit + lockout |
| Token roubado | Expiração curta + refresh |
