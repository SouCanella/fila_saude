# Visão de produto — FilaSaúde Brasil

_Versão formal — bootstrap bloco A (2026-06-09)._

---

## Identidade

| Campo | Valor |
|-------|-------|
| **Nome** | FilaSaúde Brasil |
| **Domínio provisório** | `filasaude.br` (registro pendente) |
| **Repositório** | `fila_saude` |
| **Responsável produto** | Romulo Canella |
| **Idioma documentação** | pt-BR |

---

## Pitch (uma frase)

**Plataforma nacional mobile-first que mostra filas de emergência hospitalares por especialidade, ajudando o cidadão a escolher a unidade mais próxima com menor espera — com rota, avaliação pública e transparência da fonte de dados.**

---

## Problema

Quem precisa de emergência hospitalar decide para onde ir **sem informação em tempo quase real** sobre filas, especialidades disponíveis ou tempo de deslocamento. Painéis existentes (como o do Distrito Federal) são **locais** e não oferecem, ao cidadão de outras regiões, uma experiência unificada com localização e rota.

---

## Solução

Exibir, em interface simples e mobile-first:

- Hospitais próximos à localização do usuário (ou endereço informado)
- Fila atual por **especialidade** e **classificação de risco** (protocolo Manchester)
- Tempos médios de espera (24h e 7 dias)
- **Ranking** de melhor opção (fila + distância + trânsito + avaliação Google)
- **Rota** e tempo estimado até o hospital escolhido
- **Fonte**, horário da última atualização e status da integração

---

## Para quem

| Segmento | Benefício |
|----------|-----------|
| Cidadão / familiar | Decidir mais rápido para onde ir |
| Gestor público / rede | Visibilidade de gargalos e qualidade das integrações |
| Parceiros de dados | Canal nacional padronizado para publicar filas |

---

## Princípios de produto

1. **Clareza** acima de excesso de dados — usuário em stress cognitivo
2. **Segurança** acima de conversão — nunca substituir triagem médica
3. **Transparência** — fonte e frescor sempre visíveis
4. **Privacidade** — zero exposição de dados pessoais de pacientes
5. **Escalabilidade de dados** — arquitetura de adapters para múltiplas fontes nacionais

---

## Métrica norte

**Tempo até o usuário identificar uma opção de atendimento adequada** (clique em detalhe ou rota).

### Métricas auxiliares

- Taxa de permissão de localização
- Cliques em “Ver rota”
- Hospitais comparados por sessão
- Alertas criados (localStorage no MVP)
- % fontes atualizadas dentro do SLA (5 min alvo)
- Cobertura por UF e especialidade

---

## Escopo MVP (resumo)

**In:** mapa, lista, detalhe, comparar, rota, favoritos/alertas simples (localStorage), avisos legais, painel admin de integrações, dados simulados ou piloto regional (RJ).

**Out:** login obrigatório, prontuário, agendamento, IA clínica, app nativo v1, integração nacional sem contrato, push notifications.

---

## Referências

- Mockups: [`design-references/screens/`](../design-references/screens/)
- Discovery: [`docs/discovery/product-discovery.md`](discovery/product-discovery.md)
- Arquitetura: [`docs/02-architecture.md`](02-architecture.md)
- Referência mercado: [Portas SHE — DF](https://clst.saude.df.gov.br/)

---

## Evolução pós-MVP

- PWA instalável → app nativo
- Push notifications para alertas de fila
- Painel B2G/B2B (analytics regionais, licenciamento)
- Mais UFs e hospitais privados com integração contratada
- i18n se necessário
