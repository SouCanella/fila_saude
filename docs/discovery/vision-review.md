# Revisão de visão e escopo (fase 0)

_Checklist humano antes de `discovery.status: complete`. Não substitui [requirements-review.md](requirements-review.md) (fase 2 — planejamento MVP)._

**Status da discovery:** `complete` — aprovado em 2026-06-09.

---

## Projeto

- [x] **Nome provisório acordado:** FilaSaúde Brasil (repo: `fila_saude`)
- [x] **Problema claro:** cidadão sem visibilidade nacional das filas de emergência por especialidade
- [x] **Usuário-alvo MVP:** pessoa buscando atendimento de emergência (ou familiar)
- [x] **Referência:** painel DF ([clst.saude.df.gov.br](https://clst.saude.df.gov.br/)) — evoluir para escopo nacional com localização e rota
- [x] **Escopo MVP narrativo** definido em [`product-discovery.md`](product-discovery.md) (incluído / fora)
- [x] **Mockups funcionais** revisados e **aprovados** em [`design-references/screens/`](../../design-references/screens/) — `design.status: approved` (2026-06-09)

---

## Decisões propostas (confirmar ou ajustar)

| # | Decisão | Proposta |
|---|---------|----------|
| 1 | Plataforma inicial | Web responsiva mobile-first → PWA/app depois |
| 2 | Recorte geográfico MVP | Piloto RJ (mockups) → expansão nacional; dados simulados/reais |
| 3 | Diferencial | Ranking fila + distância + trânsito + Google rating + frescor do dado |
| 4 | Mapas | Google Maps Platform (crédito MVP ~US$ 200/mês) |
| 5 | Infra local | Docker Compose (web, api, postgres, redis) |
| 6 | Login usuário final | Não no MVP |
| 7 | Ética | Não substitui triagem médica — avisos visíveis |
| 8 | LGPD | Localização com consentimento; sem dados de pacientes |

---

## Telas MVP (`design-references/screens/`)

- [x] Início (`index.html`)
- [x] Onboarding / localização (`onboarding.html`)
- [x] Mapa com filtros (`mapa.html`)
- [x] Lista detalhada (`lista.html`)
- [x] Detalhe do hospital (`hospital.html`)
- [x] Comparar hospitais (`comparar.html`)
- [x] Rota e tempo estimado (`rota.html`)
- [x] Favoritos e alertas (`alertas.html`)
- [x] Status integrações — admin (`admin-status.html`)
- [x] Sobre / segurança (`sobre.html`)

---

## Stack (hints — detalhe em `bootstrap-hints.md`)

- [x] Frontend: Next.js + TypeScript + Tailwind
- [x] Backend: FastAPI **ou** NestJS (escolher no bootstrap)
- [x] DB: PostgreSQL + PostGIS; cache Redis
- [x] Dev: Docker Compose
- [x] Contratos: OpenAPI first

---

## Pontos de atenção (aceitos como riscos conhecidos?)

- [x] Dados nacionais não padronizados — adapters por fonte
- [x] Custo/limites Google Maps em escala — monitorar billing
- [x] Responsabilidade médica — copy e termos antes de produção
- [x] Integrações reais exigem contrato jurídico com fontes

---

## Próximo passo técnico

- [x] Hints de stack registrados em [`bootstrap-hints.md`](bootstrap-hints.md)
- [x] Sem bloqueio conhecido para iniciar **bootstrap A–N**
- [x] Design aprovado em `design-references/APPROVAL.md` — próximo: **bootstrap** → **planejamento MVP**

---

## Confirmação

| Campo | Valor |
|-------|-------|
| Revisor | Romulo Canella |
| Data | 2026-06-09 |
| Status | **ok** |
| Ajustes solicitados | — |

**Depois:** skill **project-bootstrap** (A–N) → **planejamento MVP** (`project-mvp-planning`) → entrega.
