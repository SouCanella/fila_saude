# FilaSaúde API (Go)

REST API + jobs de ingestão.

## Desenvolvimento local

```bash
# Infra
docker compose up -d postgres redis
docker compose --profile routing up -d osrm

# Variáveis (raiz do monorepo)
export DATABASE_URL=postgresql://filasaude:filasaude@localhost:5432/filasaude
export REDIS_URL=redis://localhost:6379/0
export OSRM_BASE_URL=http://localhost:5000
export APP_PORT=8000

# Migrations
cd apps/api && go run ./cmd/migrate

# Servidor
go run ./cmd/server
```

## Testes

```bash
# Unitários
go test ./...

# Integração (requer compose)
export DATABASE_URL=... REDIS_URL=... OSRM_BASE_URL=...
go test -tags=integration ./tests/integration/...
```

## Logs (REQ-014)

JSON em stdout via `slog`: `request_id`, `method`, `path`, `status`, `duration_ms`, `level`, `msg`.
