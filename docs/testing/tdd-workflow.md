# Workflow TDD

## Ciclo universal

1. Spec aprovada + plano de testes (camadas marcadas na spec)
2. Escrever teste → **red**
3. Código mínimo → **green**
4. Refactor
5. Camadas adicionais conforme matriz abaixo (integração inclui contrato OpenAPI, E2E)
6. Docs + delivery-log

---

## Quais testes fazer? (matriz por impacto)

Use a spec (`Impactos` + checkboxes em **Camadas de teste**) para decidir o pacote **antes** de codificar. O humano confirma na aprovação da spec.

| A REQ tem… | Obrigatório no mínimo | Opcional |
|------------|----------------------|----------|
| Regra de negócio / domínio (back) | Unitário **back** | — |
| Endpoint novo ou alterado (`openapi_operations`) | Unitário back + **integração** (inclui **contrato** OpenAPI) | — |
| Tela / componente (`mock_screens`, impacto Front) | Unitário **front** (componente/hook) | Contrato se consome API |
| Fluxo crítico (`critical_flow: true`) | Tudo acima que se aplicar + **E2E** | — |
| Só ajuste visual (sem lógica) | Unitário front do comportamento afetado | E2E se fluxo crítico |
| Bugfix | Teste na camada que reproduz o bug | Regressivo completo ao fechar |

**E2E:** só se `critical_flow: true` na spec **e** `e2e.enabled: true` em `project.config.yaml`. Fluxos críticos típicos: login, pagamento, cadastro sensível — definidos no bootstrap (bloco L).

**Não fazer:** E2E em toda feature; unitário front em REQ só back; integração sem endpoint na OpenAPI.

---

## Ordem TDD (feature full stack)

Quando back + front + API na mesma REQ:

1. OpenAPI (contract-first) se endpoint novo
2. Unitário back → red → green
3. Integração API (incl. contrato OpenAPI) → red → green
4. Unitário front → red → green
5. E2E se `critical_flow: true` → red → green
6. Regressivo completo (suite do projeto)

REQ só back ou só front: seguir apenas as linhas aplicáveis da matriz.

---

## Por tipo de mudança

### Regra de negócio (back)

Teste domínio/use case → implementação → integração (incl. contrato OpenAPI) se expuser API.

### Endpoint novo (contract-first)

OpenAPI → teste de integração/contrato falhando → implementação → green. Assertar erros do [error-catalog](../api/error-catalog.md).

### Componente UI (após HTML aprovado)

Teste componente/hook → implementação fiel ao HTML → testes de comportamento.

### Bugfix

Teste reproduz bug na camada adequada → correção → teste permanece no regressivo.

---

## Evidência

Registrar no [delivery-log](../delivery-log.md): comando, red/green, camadas executadas (unit back, unit front, integração incl. contrato, E2E), % cobertura do módulo.

**Scaffold:** `make quality-scaffold --req REQ-XXX` gera stubs a partir das tabelas da spec (TDD red). Incluir `@req REQ-XXX` no nome do teste para o export CI ligar ao painel.

---

## HTML mock ≠ TDD

Protótipo em `design-references/` não substitui testes do código real.
