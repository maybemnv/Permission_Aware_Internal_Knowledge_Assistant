# Production-ready repository baseline

Use `APP_ENV=local-fixture APP_MODE=fixture` for the deterministic demo. Staging
and production require `APP_MODE=postgres`, a PostgreSQL/pgvector
`DATABASE_URL`, `SEARCH_PROVIDER=postgres`, `QUEUE_PROVIDER=redis` (or
`celery`), `REDIS_URL`, `AUTH_BEARER_TOKEN`, and `AUTH_PRINCIPAL_KEY`.

```powershell
uv run --extra postgres python -c "from pathlib import Path; import psycopg; psycopg.connect(__import__('os').environ['DATABASE_URL']).close()"
psql "$env:DATABASE_URL" -f db/migrations/001_initial.sql
uv run uvicorn apps.api.main:app --host 0.0.0.0 --port ${env:PORT ?? 8102}
```

The production API never accepts `X-Demo-Principal`; it resolves the configured
principal through the bearer-token boundary and PostgreSQL ACL/group tables.
Authorization is applied before model context construction and source preview.
Connector sync work must use the configured durable queue; inline fixture work
is rejected outside local-fixture mode. Provider credentials and connector
activation remain deployment work.
