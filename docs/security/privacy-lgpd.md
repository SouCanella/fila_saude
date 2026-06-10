# LGPD / Privacidade — FilaSaúde Brasil

Preenchido no bootstrap (bloco N — 2026-06-09).

## Aplicabilidade

**Sim** — tratamento de dados pessoais limitados (localização consentida, favoritos locais, logs agregados).

## Dados pessoais tratados

| Categoria | Finalidade | Base legal | Retenção |
|-----------|------------|------------|----------|
| Geolocalização (browser) | Ranking e rota de hospitais | Consentimento (Art. 7º, I) | Não persistir no servidor MVP; só em sessão/cliente |
| Favoritos / alertas | UX personalizada | Legítimo interesse / consentimento | localStorage — dispositivo do usuário |
| Logs agregados (IP mascarado) | Segurança e operação | Legítimo interesse | 90 dias |
| Credenciais admin | Painel de integrações | Execução de contrato / obrigação legal | Conta ativa + 30 dias pós revogação |

## Dados **não** coletados no MVP

- Dados de saúde do usuário
- Identificação de pacientes nas filas hospitalares
- Prontuário ou histórico clínico
- Conta obrigatória do cidadão

## Transparência na UI

Telas `onboarding.html` e `sobre.html` explicam:

- Uso da localização e como revogar (configurações do browser)
- Limites do serviço (não substitui triagem médica)
- Fonte e frescor dos dados

## Na spec

Se a feature tocar PII: marcar impacto LGPD e revisar este documento antes de implementar.

## Direitos do titular

Procedimento MVP: canal `contato@filasaude.br` (provisório) — prazo de resposta 15 dias úteis.

Direitos: confirmação, acesso, correção, eliminação, portabilidade quando aplicável.

## Registro

Manter decisões em ADR quando política de retenção ou novas categorias de dados forem introduzidas.

## Referências

- Mockup: [`design-references/screens/sobre.html`](../../design-references/screens/sobre.html)
- Segurança: [security-checklist.md](security-checklist.md)
