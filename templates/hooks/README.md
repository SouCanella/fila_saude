# Pre-commit hooks

Instalar após bootstrap (bloco B — stack).

## Objetivo

Falhar cedo antes do CI: lint, format, secrets leve.

## Husky (Node)

```bash
npm install -D husky lint-staged
npx husky init
```

Exemplo `.husky/pre-commit`:

```sh
#!/bin/sh
npm run lint
npm test -- --passWithNoTests --findRelatedTests --bail
```

## Outras stacks

Adaptar equivalente (pre-commit framework Python, etc.).

CI permanece porteiro final — ver `templates/ci/README.md`.
