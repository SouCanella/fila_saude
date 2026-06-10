# Snippets Docker — FilaSaúde Brasil

Gerado no bootstrap (bloco C — 2026-06-09).

| Arquivo | Uso |
|---------|-----|
| [`../../docker-compose.yml`](../../docker-compose.yml) | Dev local — postgres (PostGIS), redis; web/api com profile `full` |
| `.env.example` | Variáveis de ambiente |

## Uso rápido

```bash
cp .env.example .env
docker compose up -d postgres redis
# Após scaffold de apps:
docker compose --profile full up -d
```

## Imagens

- `postgis/postgis:16-3.4` — PostgreSQL + PostGIS
- `redis:7-alpine` — cache de snapshots

Dockerfiles de `apps/web` e `apps/api` serão criados no primeiro card de infraestrutura.
