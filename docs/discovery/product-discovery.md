# Descoberta do produto — FilaSaúde Brasil

_Status: confirmado_  
_Data: 2026-06-09_  
_Responsável: Romulo Canella_

> Referência de mercado: [Portas do Serviço Hospitalar de Emergência — DF](https://clst.saude.df.gov.br/)  
> Mockups funcionais: [`design-references/screens/`](../../design-references/screens/) (HTML estático, dados simulados RJ).

---

## 1. Objetivo do produto

Criar uma **plataforma nacional**, inicialmente **web mobile-first** (com evolução para PWA/app), que permita ao cidadão **visualizar a situação das filas das portas de emergência hospitalares** — por hospital, especialidade e classificação de risco — e **escolher a unidade mais adequada** com base em:

- **Menor fila** na especialidade desejada (ex.: Pediatria, Clínica Médica, Ortopedia)
- **Proximidade** e **tempo estimado de deslocamento** (rota)
- **Avaliação pública** do hospital (Google Places, quando disponível)
- **Confiabilidade e frescor** dos dados (fonte, última atualização, status da integração)

**Sucesso em 6–12 meses (hipótese):** cobertura piloto em 2–3 UFs com fontes públicas ou integrações autorizadas; usuários conseguem identificar uma opção adequada em menos de 60 segundos; dados atualizados dentro de SLA acordado (alvo: 5 min quando a fonte permitir).

---

## 2. Problema que resolve

Hoje, quem precisa de atendimento de emergência decide **no escuro**: vai ao hospital mais próximo, ao de costume ou ao que alguém indicou — sem saber se a fila está alta, se a especialidade está disponível ou se outra unidade a poucos minutos a mais oferece espera menor.

O DF já publica um painel evoluído (mapa, cards por hospital, especialidades, classificação de risco, totais aguardando, tempos médios 24h/7d). **Não existe equivalente nacional unificado**, acessível ao cidadão com localização, rota e ranking de decisão.

---

## 3. Público e personas

| Persona | Necessidade | Prioridade MVP |
|---------|-------------|----------------|
| **Usuário final** (paciente ou familiar) | Decisão rápida, linguagem simples, mapa/lista, rota, aviso de segurança | **Alta** |
| **Gestor público / rede hospitalar** | Monitorar cobertura, atraso de integração, gargalos por UF/especialidade | Média (painel interno) |
| **Parceiro de dados** (secretaria, hospital, integrador) | Adapter por fonte, auditoria, SLA de atualização | Média (backend/ops) |

---

## 4. Escala esperada

| Dimensão | MVP | Evolução |
|----------|-----|----------|
| **Usuários simultâneos** | Baixa/média (piloto regional) | Nacional — picos em surtos/epidemias |
| **Hospitais** | Dezenas (1–2 UFs piloto) | Centenas/milhares |
| **Fontes de dados** | 1–3 adapters (ex.: DF TrakCare, API municipal) | Múltiplas UFs, nomenclaturas normalizadas |
| **Atualização** | Alvo 5 min (quando fonte permitir) | Near real-time onde houver API |
| **Arquitetura** | Preparada para escala nacional desde o desenho (adapters, cache, geo) | — |

---

## 5. Experiência e plataformas

| Aspecto | Decisão proposta |
|---------|------------------|
| **MVP** | Site responsivo **mobile-first** |
| **Evolução** | PWA → app nativo/híbrido (Capacitor/React Native) |
| **Painel interno** | Web desktop — status de integrações e qualidade do dado |
| **Offline** | Fora do MVP; endereço manual como fallback quando GPS negado |
| **Login usuário final** | **Não** no MVP (acesso público) |

### Telas validadas (`design-references/screens/`)

| Tela | Arquivo | Função |
|------|---------|--------|
| Início | `design-references/screens/index.html` | Proposta de valor, melhores opções, KPIs |
| Onboarding | `design-references/screens/onboarding.html` | Localização, especialidade, aviso médico |
| Mapa | `design-references/screens/mapa.html` | Filtros, marcadores, modal, lista lateral |
| Lista detalhada | `design-references/screens/lista.html` | Cards por especialidade |
| Detalhe hospital | `design-references/screens/hospital.html` | Fila, risco, histórico 24h/7d, fonte |
| Comparar | `design-references/screens/comparar.html` | Matriz de decisão entre hospitais |
| Rota | `design-references/screens/rota.html` | Tempo/distância estimados, passo a passo |
| Favoritos/alertas | `design-references/screens/alertas.html` | Favoritos (localStorage); alertas simulados |
| Status integrações | `design-references/screens/admin-status.html` | Painel interno B2G/ops |
| Sobre/segurança | `design-references/screens/sobre.html` | LGPD, limites, responsabilidade |

---

## 6. Restrições e premissas

### Compliance e ética

- **Não exibir dados pessoais de pacientes** (LGPD).
- **Não substituir triagem médica** — aviso visível em todas as jornadas críticas.
- Casos graves: orientar SAMU/emergência imediata, não apenas “menor fila”.
- Produção exige: termos de uso, política de privacidade, análise jurídica, contratos com fontes.

### Dados e integrações

- Dados nacionais **não estão padronizados**; cada UF/município pode exigir adapter próprio.
- MVP de engenharia pode iniciar com **dados simulados** (como nos mockups) até contrato/fonte real.
- Google Rating e rotas dependem de **Google Maps Platform** (crédito mensal gratuito ~US$ 200 — suficiente para MVP/dev; monitorar uso).

### Equipe e prazo

- A definir no bootstrap; mockups funcionais **antes** do código de produto.
- **Docker** desejado para ambiente local (front, back, DB, cache).

### Premissas técnicas

- Localização do usuário **somente com consentimento**; preferência por processamento no cliente quando possível.
- Especialidades e classificação de risco **normalizadas** internamente (Manchester: vermelho → azul).

---

## 7. MVP — incluído (narrativo)

1. Usuário abre o site (mobile ou desktop).
2. **Onboarding:** permite localização ou informa endereço; escolhe especialidade.
3. Vê **mapa** e/ou **lista** de hospitais próximos, ordenados por “melhor opção” (fila + distância + trânsito + avaliação).
4. Abre **detalhe** do hospital: fila por classificação de risco, tempos médios 24h e 7d, fonte e horário da última atualização.
5. **Compara** até 3 hospitais lado a lado.
6. Abre **rota** com tempo estimado de deslocamento (Google Directions no produto real).
7. **Favorita** hospital e cria **alerta simples** (fila abaixo de limite) — pode ser local no MVP ou com backend leve.
8. Consulta **sobre/segurança** e vê **status de confiabilidade** da fonte por hospital.
9. **Painel interno** (admin): status dos conectores, defasagem, cobertura por UF.

### Funcionalidades sugeridas (priorizadas)

| # | Funcionalidade | Valor de negócio |
|---|----------------|------------------|
| 1 | Busca por hospital, cidade, UF | Encontrar unidade conhecida |
| 2 | Filtro por especialidade | Pediatria vs clínica vs ortopedia |
| 3 | Mapa com cards e marcadores | Visão espacial rápida |
| 4 | Lista detalhada (modelo DF) | Comparar filas e tempos médios |
| 5 | Ranking “melhor opção” transparente | Decisão em segundos |
| 6 | Detalhe: fila + risco + histórico | Confiança na escolha |
| 7 | Comparação side-by-side | Reduzir idas erradas |
| 8 | Rota + tempo (Google Directions) | Logística real |
| 9 | Avaliação Google (Places API) | Contexto qualitativo |
| 10 | Fonte + SLA + badge de frescor | Transparência |
| 11 | Favoritos e alertas de fila | Retenção e utilidade recorrente |
| 12 | Avisos médicos e SAMU | Proteção legal e ética |
| 13 | Painel status integrações | Operacional B2G |

---

## 8. MVP — fora do escopo (v1)

- Login/cadastro obrigatório para usuário final
- Prontuário, cadastro de paciente ou qualquer dado clínico individual
- Agendamento médico ou telemedicina
- Diagnóstico ou triagem por IA
- Integração nacional real **sem** validação jurídica e contrato por fonte
- App nativo nas lojas (fase pós-MVP web/PWA)
- Pagamentos ou planos premium no lançamento público

---

## 9. Hipóteses e riscos

| Risco | Mitigação proposta |
|-------|-------------------|
| Fontes de dados indisponíveis ou heterogêneas | Arquitetura de adapters; piloto por UF; dados simulados até integração |
| Dado defasado gera decisão errada | Badge de frescor, SLA visível, desabilitar hospital sem atualização recente |
| Custos Google Maps em escala | Cache de rotas; crédito MVP; avaliar Mapbox/OSM como fallback |
| Responsabilidade médica | Copy legal clara; não usar linguagem de “recomendação clínica” |
| Picos de tráfego | CDN + cache Redis + API read-heavy |
| LGPD (localização) | Consentimento explícito; minimização; política publicada |

---

## 10. Objetivos de negócio (rastreáveis — rascunho)

| ID | Objetivo | Métrica | REQ(s) futuros |
|----|----------|---------|----------------|
| O1 | Reduzir tempo até decisão | Tempo médio até clicar em rota/detalhe | REQ-006, REQ-007, REQ-008, REQ-009, REQ-010 |
| O2 | Aumentar confiança no dado | % hospitais dentro do SLA de atualização | REQ-004, REQ-013, REQ-014 |
| O3 | Cobertura geográfica | UFs e hospitais integrados | REQ-001, REQ-004 |
| O4 | Adoção mobile | % sessões mobile vs desktop | REQ-005, REQ-006, REQ-007 |

> REQs e cards definidos em **project-mvp-planning** (2026-06-10) — ver [mvp-backlog.md](../backlog/mvp-backlog.md).

---

## 11. Notas da conversa (síntese do prompt inicial)

- Produto inspirado no painel do DF, com ambição **nacional**.
- Usuário vê hospital **mais perto** e com **menor fila**; incluir **Google rating**.
- **Mockups funcionais** migrados para `design-references/` — ver bloco H bootstrap
- Stack a definir no bootstrap; sugestão preliminar: **Docker**, web moderna, **Google Maps** (tier gratuito MVP).
- Discovery **não** inclui bootstrap, planejamento de cards/REQs nem código de produto nesta fase.

---

## Próximo gate

Humano confirma checklist em [`vision-review.md`](vision-review.md) → então `discovery.status: complete` → **project-bootstrap** (A–N).
