# Design system — FilaSaúde Brasil

Preenchido no bootstrap (bloco H — 2026-06-09) a partir de `design-references/shared/`.

**Status:** mockups aprovados — `design.status: approved`, `pattern_version: 1`.

## Tokens

Ver `design-references/shared/design-tokens.css`.

| Token | Uso |
|-------|-----|
| `--brand` / `--brand-strong` / `--brand-dark` | Identidade visual, CTAs |
| `--ink` / `--muted` | Texto principal e secundário |
| `--line` / `--surface` | Bordas e fundos |
| `--green` … `--red` | Badges Manchester (risco) |
| `--radius` / `--radius-sm` | Cantos arredondados mobile-first |
| `--shadow` | Elevação de cards |
| `--max` | Largura máxima do layout |

## Componentes

Ver `design-references/shared/components.css` e `filasaude-mock.js` (comportamento).

## Acessibilidade

- WCAG 2.1 AA como meta
- `filasaude-a11y.js`: skip link, focus trap modal, tabs ARIA, toast live region
- `:focus-visible` global em elementos interativos
- Roteiro manual F1–F5 em `design-references/APPROVAL.md`

## Regras de implementação

- Pós-aprovação: UI real deve espelhar mockups aprovados
- Usar tokens CSS → migrar para Tailwind theme na implementação Next.js
- Badges de risco Manchester: contraste mínimo AA
- Nunca remover avisos médicos das telas onboarding/sobre

## Inventário de componentes

| Classe / padrão | Uso |
|-----------------|-----|
| `.navbar` / `.nav-link` | Navegação inferior mobile |
| `.filters` / `.field` | Barra de filtros (especialidade, UF, raio) |
| `.map-card` / `.mock-map` | Container do mapa |
| `.hospital-card` / `.card` | Card de hospital na lista/mapa |
| `.card-metric-row` | KPIs (distância, fila, rating) |
| `.risk-section` / `.risk-row` / `.risk` | Grid Manchester por especialidade |
| `.badge` / `.badge-*` | Status integração, frescor |
| `.tab-btn` | Tabs mapa/lista/comparar |
| `.modal` | Detalhe rápido no mapa |
| `.btn-primary` / `.btn-secondary` | Ações principais e secundárias |
| `.toast` | Feedback não bloqueante |
| `.skip-link` | A11y — pular para conteúdo |
| `.compare-table` | Matriz comparar hospitais |
| `.admin-table` | Painel status integrações |

## Telas MVP

| Arquivo | Função |
|---------|--------|
| `index.html` | Landing + melhores opções |
| `onboarding.html` | Localização + aviso médico |
| `mapa.html` | Mapa + filtros + modal |
| `lista.html` | Lista detalhada |
| `hospital.html` | Detalhe unidade |
| `comparar.html` | Comparar hospitais |
| `rota.html` | Rota e tempo |
| `alertas.html` | Favoritos/alertas (localStorage) |
| `admin-status.html` | Painel integrações |
| `sobre.html` | LGPD e limites |

Referência canônica: `design-references/screens/`.
