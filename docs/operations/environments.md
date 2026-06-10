# Ambientes — FilaSaúde Brasil

Preenchido no bootstrap (bloco M — 2026-06-09).

| Ambiente | Uso | URL base |
|----------|-----|----------|
| **local** | Desenvolvimento (Docker Compose) | Web `http://localhost:3000` · API `http://localhost:8000` |
| **staging** | Homologação; dados simulados ou sandbox de integração | `https://staging.filasaude.br` (provisório) |
| **prod** | Piloto regional (RJ inicial) | `https://filasaude.br` (provisório) |

## Desenvolvimento local

```bash
# Infra (PostGIS + Redis + OSRM dev stub)
docker compose up -d postgres redis
docker compose --profile routing up -d osrm

# Ou smoke script
./scripts/smoke-compose.sh

# Variáveis — copiar .env.example → .env (sslmode=disable no DATABASE_URL)
export DATABASE_URL=postgresql://filasaude:filasaude@localhost:5432/filasaude?sslmode=disable
export REDIS_URL=redis://localhost:6379/0
export OSRM_BASE_URL=http://localhost:5000
export APP_PORT=8000
```

Ver também `apps/api/README.md` para migrations e servidor.

Grupos principais:

- **App** — `NODE_ENV`, `APP_URL`, `API_URL`
- **Database** — `DATABASE_URL` (PostGIS)
- **Redis** — `REDIS_URL`
- **Google Maps** — `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`, `GOOGLE_MAPS_SERVER_KEY`
- **Auth admin** — `JWT_SECRET`, `ADMIN_USERS` (ou provider futuro)
- **Ingestão** — `INGESTION_INTERVAL_SECONDS`, credenciais por adapter (vault)

## Secrets

Nunca commitar `.env` com valores reais.

Produção: secrets manager do provedor cloud ou variáveis protegidas no CI/CD.

## Dados por ambiente

| Ambiente | Dados |
|----------|-------|
| local | Mock RJ (13 hospitais) + seed SQL |
| staging | Simulados ou sandbox de APIs públicas |
| prod | Fontes reais autorizadas (piloto) |

## Referências

- Docker: `docker-compose.yml`
- Arquitetura: [../02-architecture.md](../02-architecture.md)
