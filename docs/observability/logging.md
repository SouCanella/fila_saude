# Logs estruturados — FilaSaúde Brasil

Biblioteca: **structlog** (Python/FastAPI) + wrapper JSON no Next.js (pino ou equivalente na implementação).

Preenchido no bootstrap (bloco G — 2026-06-09).

## Campos mínimos

- `timestamp` — ISO 8601 UTC
- `level` — debug | info | warn | error
- `service` — `api` | `web` | `ingestion`
- `traceId` / `requestId` — UUID por request HTTP ou job
- `message` — texto curto
- `context` — objeto (hospital_id, adapter, uf, …)
- `error` — stack trace **somente** dev/staging

## Correlation

- Header HTTP `X-Request-Id` propagado web → api
- Jobs de ingestão herdam `traceId` do ciclo ou geram novo por execução
- Logs de adapter incluem `source_adapter` e `source_id`

## Níveis

| Nível | Uso |
|-------|-----|
| debug | Diagnóstico local |
| info | Fluxo normal (request, ingestão ok) |
| warn | Degradado recuperável (cache miss, fonte lenta) |
| error | Falha; requer ação (adapter down, DB indisponível) |

## Proibido em log (PII deny list)

- E-mail, CPF, telefone, nome completo de usuário
- Coordenadas GPS brutas do usuário (usar geohash ou omitir)
- Senhas, tokens JWT, API keys Google
- Dados clínicos ou identificação de pacientes nas filas
- IP completo em produção (mascarar último octeto se necessário)

## Métricas derivadas

- Lag de ingestão por fonte (`integration_health.lag_minutes`)
- Hospitais stale (> SLA)
- Latência p99 por endpoint
- Cache hit rate Redis

Alertas MVP (ops): integração down > 15 min; fila de ingestão parada.

## Exemplos

```json
{"timestamp":"2026-06-09T12:00:00Z","level":"info","service":"api","requestId":"abc-123","message":"Hospitals listed","context":{"count":13,"uf":"RJ","adapter":"mock_rj"}}

{"timestamp":"2026-06-09T12:05:00Z","level":"error","service":"ingestion","traceId":"job-456","message":"Adapter fetch failed","context":{"source_adapter":"df_trakcare","http_status":503}}
```

```json
// ❌ RUIM — nunca logar
{"message":"User location","lat":-22.971,"lng":-43.182,"email":"user@example.com"}
```

Correlacionar HTTP com jobs assíncronos via mesmo `traceId` quando o job for disparado por request admin.
