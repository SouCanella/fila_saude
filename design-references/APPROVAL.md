# Aprovação do padrão visual — FilaSaúde Brasil

## Status

- [ ] draft
- [ ] in_review
- [x] **approved**

Aprovado por: Romulo Canella  
Data: 2026-06-09  
pattern_version: 1

## Funcionalidades mockadas (piloto Rio de Janeiro)

| Tela | Arquivo | mocks_complete |
|------|---------|----------------|
| Início | design-references/screens/index.html | [x] |
| Onboarding / localização | design-references/screens/onboarding.html | [x] |
| Mapa com filtros | design-references/screens/mapa.html | [x] |
| Lista detalhada | design-references/screens/lista.html | [x] |
| Detalhe do hospital | design-references/screens/hospital.html | [x] |
| Comparar hospitais | design-references/screens/comparar.html | [x] |
| Rota e tempo estimado | design-references/screens/rota.html | [x] |
| Favoritos e alertas | design-references/screens/alertas.html | [x] |
| Status integrações (admin) | design-references/screens/admin-status.html | [x] |
| Sobre / segurança | design-references/screens/sobre.html | [x] |

## Assets compartilhados

| Arquivo | Função |
|---------|--------|
| `shared/design-tokens.css` | Tokens de cor, raio, sombra |
| `shared/components.css` | Layout, componentes e `:focus-visible` |
| `shared/filasaude-mock.js` | Dados simulados (RJ) + renderização das telas |
| `shared/filasaude-a11y.js` | Skip link, modal trap, tabs teclado, live region |

## Checklist geral

- [x] Todos os botões e links funcionam
- [x] Filtros e navegação entre telas do MVP sem 404
- [x] Dados simulados — hospitais do Rio de Janeiro
- [x] Loading / erro / vazio testáveis em todas as telas
- [x] Sem botões mortos ou TODO visual

### Estados de UI (`?state=`)

Barra **Demo UI** abaixo da navegação em todas as telas. Valores:

| Parâmetro | Efeito |
|-----------|--------|
| _(ausente)_ | Fluxo normal |
| `?state=loading` | Skeleton / carregando |
| `?state=error` | Painel de erro + “Tentar novamente” |
| `?state=empty` | Estado vazio + ação sugerida |

Exemplos: `mapa.html?state=loading`, `hospital.html?id=invalido` (erro por ID inválido).

## Acessibilidade (a11y)

- [x] Contraste WCAG AA alvo (badges de risco)
- [x] Foco visível em interativos (`:focus-visible` em links e botões)
- [x] Labels em inputs de filtro (`for` / `id` no mapa)
- [x] `lang="pt-BR"` no `<html>`
- [x] Navegação por teclado nos fluxos críticos

### Fluxos críticos — roteiro de teste manual

| ID | Fluxo | Passos (somente teclado) |
|----|-------|----------------------------|
| **F1** | Decisão rápida | `index.html` → Tab até skip link (opcional) → Tab até "Abrir mapa" → Enter → Tab nos filtros → Tab até marcador no mapa → Enter abre modal → Tab circula dentro do modal → Esc fecha e devolve foco → Tab "Ver rota" → Enter |
| **F2** | Filtros mapa/lista | `mapa.html` / `lista.html` → Tab entre busca, especialidade, UF, ordenar → Enter em "Usar localização" ou links de ação |
| **F3** | Detalhe com abas | `hospital.html?id=hmlj` → Tab até abas → ←/→ move foco entre abas → Enter/Space ativa aba → painel correspondente visível |
| **F4** | Navegação global | Qualquer tela → Tab → skip link "Ir para o conteúdo" visível ao focar → Enter → foco em `#main-content` → nav principal por Tab |
| **F5** | Cards de hospital | `lista.html` → Tab até "Favoritar" ou "Detalhes" → Enter/Space ativa |

### Replicação no app real (Next.js)

- **Skip link** no layout raiz (`href="#main-content"`)
- **Dialog** com focus trap (Radix Dialog / shadcn)
- **Tabs** com roving `tabIndex` (Radix Tabs)
- **Marcadores de mapa** como `<button>` com `aria-label` descritivo
- Regressão: repetir roteiro F1–F5 em testes E2E (fase pós-MVP)

## Componentes

- [x] `shared/design-tokens.css` + `shared/components.css` + `shared/filasaude-mock.js` + `shared/filasaude-a11y.js`

### Exceções locais

| Tela | Justificativa |
|------|---------------|
| — | Nenhuma |

## Aprovação explícita

Ao aprovar, diga na IDE: *"Aprovo o padrão visual"* para atualizar `project.config.yaml` (`design.status: approved`).
