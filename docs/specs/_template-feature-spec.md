---
id: REQ-XXX
title: Nome da feature
status: draft  # draft | in_review | approved
approved_at: null
approved_by: null
req_kind: functional  # functional | non_functional
critical_flow: false  # true = E2E obrigatório
sensitive: false      # true = threat model obrigatório
card_ids: []          # CARD-001 — unidade de trabalho (obrigatório após descoberta)
openapi_operations: []
mock_screens: []
visual_reference: null  # design-references/screens/...
---

# REQ-XXX — Nome da feature

## Objetivo

## Escopo incluído

## Escopo fora

## Regras de negócio

## Critérios de aceite

- [ ]

## Cenários de sucesso

## Cenários de erro

## DoR checklist

- [ ] Objetivo claro
- [ ] Aceite testável
- [ ] Cenários erro definidos
- [ ] Impacto técnico estimado
- [ ] Estratégia de teste (camadas conforme [../testing/tdd-workflow.md](../testing/tdd-workflow.md))
- [ ] `critical_flow` definido (humano confirma se fluxo exige E2E)
- [ ] Dependências mapeadas
- [ ] HTML mock (se UI)
- [ ] OpenAPI (se API)

## Camadas de teste (preencher na spec)

Marque o que se aplica a esta REQ (ver matriz em [../testing/tdd-workflow.md](../testing/tdd-workflow.md)):

- [ ] Unitário back (domínio / use case)
- [ ] Unitário front (componente / hook)
- [ ] Integração API (inclui contrato OpenAPI e erros do error-catalog)
- [ ] E2E (`critical_flow: true` + `e2e.enabled` no config)

## Plano de testes (TDD)

### Unitários — back

| Caso | Arquivo teste | Status |
|------|---------------|--------|
| | | pending / n/a |

### Unitários — front

| Caso | Arquivo teste | Status |
|------|---------------|--------|
| | | pending / n/a |

### Integração API (inclui contrato OpenAPI)

| Endpoint / fluxo | Cenários (sucesso + erros doc) | Arquivo teste | Status |
|------------------|--------------------------------|---------------|--------|
| | | | pending / n/a |

### E2E (obrigatório se `critical_flow: true`)

| Fluxo de negócio | Persona | Passos (resumo) | Resultado esperado | Arquivo teste | Status |
|------------------|---------|-----------------|--------------------|---------------|--------|
| | | | | | pending / n/a |

## Impactos

- API:
- DB:
- Front:
- Segurança / LGPD:
- Observabilidade:

## Threat model (se sensitive: true)

Ver [../security/threat-model-template.md](../security/threat-model-template.md)
