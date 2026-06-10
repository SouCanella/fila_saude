# Protótipo HTML mockado — FilaSaúde Brasil

Contrato visual **executável no navegador**. Piloto **Rio de Janeiro** — dados simulados.

## Abrir localmente

```bash
python3 -m http.server 8080 --directory design-references
# http://localhost:8080/screens/index.html
```

Ou abra `screens/index.html` direto no navegador.

## Estrutura

| Pasta / arquivo | Função |
|-----------------|--------|
| `shared/design-tokens.css` | Tokens visuais |
| `shared/components.css` | Componentes e layout |
| `shared/filasaude-mock.js` | Hospitais RJ + lógica das telas |
| `shared/filasaude-a11y.js` | Navegação por teclado (skip, modal, tabs) |
| `screens/*.html` | Uma HTML por tela MVP |
| `APPROVAL.md` | Checklist humano + a11y |

## Telas MVP

- `index.html` — Início
- `onboarding.html` — Localização
- `mapa.html` — Mapa e filtros
- `lista.html` — Lista por especialidade
- `hospital.html` — Detalhe
- `comparar.html` — Comparação
- `rota.html` — Rota simulada
- `alertas.html` — Favoritos e alertas
- `admin-status.html` — Status integrações
- `sobre.html` — Segurança e LGPD

## Ciclo

`draft` → `in_review` → `approved` (ver `project.config.yaml` → `design`)

Status também no Project Hub: `make hub-serve` → `#design`, `#a11y`.

## Testar a11y (teclado)

Abra `screens/index.html` **sem mouse** e siga o roteiro em [`APPROVAL.md`](APPROVAL.md) (fluxos F1–F5):

1. **F4:** Tab → link "Ir para o conteúdo" → Enter
2. **F1:** Tab até mapa → marcador → Enter (modal) → Esc (fecha)
3. **F3:** `hospital.html?id=hmlj` → abas com ←/→ e Enter

Padrões implementados em `shared/filasaude-a11y.js` — replicar no app real (Dialog + Tabs acessíveis).

## Nota

A pasta legada `mockups/` na raiz foi descontinuada — use apenas `design-references/`.
