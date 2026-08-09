# Deployment Handoff

## Scope and evidence status

This document separates a client demo, staging, and a production-like deployment shape. It does not provision infrastructure, select a vendor contract, or certify production readiness. The current checkout has local FastAPI/web/fixture, connector-registry, and worker contracts plus migration and seed artifacts; no external infrastructure or long-lived worker deployment is configured, so all commands and external checks must be verified in the target environment.

The design names Supabase managed PostgreSQL with pgvector as the preferred database direction. Search, queue, hosting, domains, secret management, monitoring, backups, connector credentials, provider scopes, billing, and TLS remain deployment choices and client-owned verification work.

## Deployment tiers

| Tier | Intended use | Database/search | Queue/worker | Evidence boundary |
|---|---|---|---|---|
| Client-demo prototype | Repeatable review of the permission and evidence journey | Fixture mode; disposable local PostgreSQL or Supabase project if useful; Postgres-only search is sufficient | Inline/local worker or Supabase jobs for low volume | Fixture behavior is demonstrable; live provider, browser, DNS, TLS, backup, and scale claims remain `unverified` |
| Staging | Controlled integration tests with client-owned test tenants | Supabase PostgreSQL + pgvector; managed or self-hosted OpenSearch if selected | Redis-backed worker or Supabase jobs with leases/idempotency | Provider scopes, ACL fidelity, sync/recovery, observability, restore, and domain checks require fresh evidence |
| Production-like | Architecture rehearsal before a real go-live decision | Managed Supabase PostgreSQL + pgvector and an explicitly selected search provider | Separately hosted API/worker with the selected durable queue | Must have an owner, change record, monitoring, backups, restore test, rollback evidence, and live connector verification; this document makes no such claim |

Do not skip the staging boundary by pointing fixture commands, demo seed data, or unverified connectors at a shared or production-like database.

## Supabase PostgreSQL and pgvector setup

Supabase is the preferred database option from the design, not a provisioned resource in this checkout. A client or deployment owner must:

1. Create or select a Supabase project, region, billing plan, retention policy, and data-residency decision. Record the project reference without putting credentials in this repository.
2. Enable PostgreSQL `vector`/pgvector support before applying migrations that create embedding columns. Verify the extension and migration version with a read-only database check.
3. Use a private server-side database credential for API and worker runtime. Use pooled connections for web/API traffic and a direct connection for migrations where the selected Supabase plan supports both.
4. Keep the application authorization layer mandatory. Supabase Row Level Security may be defense in depth, but it cannot replace tenant, principal, ACL, lifecycle, and request-time checks before reranking or model context construction.
5. Restrict database network access, rotate credentials through the secret manager, and record the approved connection/role policy.
6. Verify backups, point-in-time recovery, restore permissions, and restore-test cadence against the selected plan before calling the tier production-like.

Illustrative verification commands, to be run only against an approved target, are:

```powershell
psql $env:DATABASE_URL -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql $env:DATABASE_URL -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
psql $env:DATABASE_URL -f db/migrations/001_initial.sql
```

The migration SQL exists in this checkout, but applying and verifying it against Supabase or another target remains `unverified`. Never place a database password or full connection string in a command transcript, ticket, screenshot, or committed file.

## Search provider choices

Choose one provider per environment and record the tradeoff:

| Option | Use when | Required operational checks | Caveat |
|---|---|---|---|
| Managed OpenSearch | Production-like lexical/vector search, managed scaling, and centralized operations are desired | Endpoint/authentication, index versioning, private networking, snapshots, query latency, ACL-safe filtering, and restore | Service cost, provider-specific vector/lexical behavior, and ACL/query tuning need live verification |
| Self-hosted OpenSearch | A controlled prototype or staging environment can operate a persistent search cluster | Persistent volumes, node health, resource limits, TLS/auth, snapshots, upgrades, index rebuild, and alerting | The team owns patching, capacity, failure recovery, and snapshot restore |
| Postgres-only | Client demo or low-volume deployment values fewer services and accepts simpler search | PostgreSQL full-text search, pgvector extension/version, indexes, query latency, connection pool, and rebuild procedure | Search scale and relevance may be lower; no production-like performance claim is implied |

The search provider must filter by tenant and permission metadata before reranking and answer context construction. A database or search-side filter is not a substitute for the server authorization check.

## Queue and worker choices

### Redis-backed queue

Use a Redis endpoint and separately hosted worker for sync, normalization, ACL refresh, deletion reconciliation, indexing, and evaluation jobs. Define leases, idempotency keys, retry classes, dead-letter handling, queue lag alerts, and shutdown behavior. Redis is a queue dependency, not the durable source of truth for tenant, ACL, source, audit, or tombstone state.

### Supabase jobs

For a low-volume demo, use Supabase-backed job tables plus scheduled invocations if the selected implementation supports them. Application code must own leases, idempotency keys, stale-job recovery, and safe retry boundaries. Confirm scheduler limits, transaction semantics, and operational visibility with the client before selecting this option.

The current prototype has no provider write-back actions. Do not blindly retry an ambiguous non-idempotent provider write if a later implementation adds one; retry only explicitly replay-safe reads/jobs.

## Hosting the web, API, and worker

Keep the three runtime boundaries separate even if one host runs them initially:

| Boundary | Suitable hosting shape | Placement rules |
|---|---|---|
| Web | Managed static/SSR web host or a container behind an HTTPS edge | Only the public API origin may be browser-visible; no database, model, queue, connector, or admin secrets in the bundle |
| API | Managed container/app service, private container platform, or controlled VM | Enforce authz, safe errors, request-time preview rechecks, TLS, redacted logs, health/readiness, and server-side model/connector access |
| Worker | Separate managed worker process, container job, or controlled VM process | Keep queue/database/connector secrets server-side; expose heartbeat and job metrics; isolate connector failures |

Hosting vendor, region, autoscaling, instance size, billing, private networking, and on-call coverage are client-owned selections. The documentation does not claim that any host is configured or that a target will meet a particular latency or SLA.

## Domains and TLS

The deployment owner must choose the public web and API domains, DNS provider, certificate ownership, and renewal path. The handoff should include:

1. DNS records or delegated zones for web and API, with the client approving the exact target values.
2. TLS certificates at the selected edge/host and automatic renewal monitoring.
3. HTTPS from browser to API and TLS for service-to-service connections where supported.
4. CORS/origin policy restricted to the approved web domain; no wildcard production policy without review.
5. Health checks that use the API origin and do not expose content.
6. A DNS/TLS test from the intended browser network, recorded as `pass` or `unverified` with date and owner.

DNS, domain registration, certificate billing, WAF/CDN policy, and client approval are external prerequisites. Do not use `example.invalid` values as real deployment settings.

## Secret inventory

The following names are the server-side handoff inventory. They are names only; values belong in a local untracked `.env`, a migration-time secure shell, or the selected host secret manager. Every example value below is intentionally `[REDACTED_SECRET]`; never replace that text with a real value in this repository.

```dotenv
DATABASE_URL=[REDACTED_SECRET]
SUPABASE_POOLER_URL=[REDACTED_SECRET]
SUPABASE_DIRECT_URL=[REDACTED_SECRET]
SUPABASE_SERVICE_ROLE_KEY=[REDACTED_SECRET]
REDIS_URL=[REDACTED_SECRET]
OPENSEARCH_PASSWORD=[REDACTED_SECRET]
OPENAI_API_KEY=[REDACTED_SECRET]
ANTHROPIC_API_KEY=[REDACTED_SECRET]
APP_SECRET_KEY=[REDACTED_SECRET]
ADMIN_TOKEN=[REDACTED_SECRET]
CONNECTOR_CREDENTIALS_ENCRYPTION_KEY=[REDACTED_SECRET]
GOOGLE_DRIVE_CLIENT_SECRET=[REDACTED_SECRET]
SHAREPOINT_CLIENT_SECRET=[REDACTED_SECRET]
SLACK_BOT_TOKEN=[REDACTED_SECRET]
TEAMS_CLIENT_SECRET=[REDACTED_SECRET]
NOTION_TOKEN=[REDACTED_SECRET]
CONFLUENCE_CLIENT_SECRET=[REDACTED_SECRET]
JIRA_API_TOKEN=[REDACTED_SECRET]
GITHUB_APP_PRIVATE_KEY=[REDACTED_SECRET]
```

Non-secret identifiers and endpoints may include `OPENSEARCH_URL`, `OPENSEARCH_INDEX`, `OPENSEARCH_USERNAME`, `NEXT_PUBLIC_API_BASE_URL`, `GOOGLE_DRIVE_CLIENT_ID`, `SHAREPOINT_CLIENT_ID`, `TEAMS_CLIENT_ID`, `CONFLUENCE_CLIENT_ID`, `GITHUB_APP_ID`, `APP_ENV`, `APP_MODE`, `API_HOST`, `API_PORT`, `DB_SSL_MODE`, `DEMO_PRINCIPAL`, `MODEL_NAME`, `ADMIN_PRINCIPAL_KEYS`, `AUDIT_RETENTION_DAYS`, `SEARCH_PROVIDER`, `QUEUE_PROVIDER`, and `MODEL_PROVIDER`. Do not put credentials inside an endpoint URL.

| Secret | Runtime placement | Owner and verification |
|---|---|---|
| `DATABASE_URL` | API/worker; direct migration process only when needed | Client/deployment database owner; verify pooling, TLS, role, rotation, and backup plan |
| `SUPABASE_POOLER_URL` / `SUPABASE_DIRECT_URL` | API/worker/migration when Supabase is selected | Client Supabase owner; verify pooled runtime/direct migration behavior and rotation |
| `SUPABASE_SERVICE_ROLE_KEY` | API/worker only, if the selected Supabase integration requires it | Client Supabase owner; never web-visible; confirm least-privilege alternative |
| `REDIS_URL` | API/worker when Redis is selected | Queue owner; verify TLS, auth, persistence decision, and network policy |
| `OPENSEARCH_PASSWORD` | API/worker when OpenSearch is selected | Search owner; verify auth, private networking, and rotation |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | API/worker only, according to `MODEL_PROVIDER` | Client model-account owner; verify model approval, spend limits, data policy, and live request behavior |
| `APP_SECRET_KEY` | API/worker secret manager, if the selected implementation uses it | Client security owner; verify rotation and invalidation behavior |
| `ADMIN_TOKEN` | API/operator channel only if selected | Client security owner; define expiry, rotation, audit, and emergency revocation |
| `CONNECTOR_CREDENTIALS_ENCRYPTION_KEY` | API/worker secret manager | Client security owner; verify envelope/storage policy and rotation recovery |
| Connector-specific secrets | Connector service/API/worker only | Client provider owner; verify tenant consent, scopes, test data, ACL mapping, rate limits, and deletion behavior |

The eight connectors and their required live checks are in [CONNECTOR_MATRIX.md](CONNECTOR_MATRIX.md). Client-owned credentials, provider scopes, data-access approvals, billing, and live verification are prerequisites, not hidden assumptions.

## Environment placement

- Browser-visible: `NEXT_PUBLIC_API_BASE_URL` only, plus non-sensitive build labels if needed.
- API: database/search/queue/model/admin/connector settings and server-side secrets.
- Worker: database/search/queue/model/connector settings and server-side secrets.
- Migration/seed job: direct database connection and migration-only credentials for the duration of the operation.
- Web host: public configuration only; never inject server secrets into a web build.
- Secret manager: production-like values, rotation metadata, access policy, and audit trail.
- Local development: untracked `.env` or process environment; the current `.env.example` contains empty values/defaults only, and no real values belong in a replacement.

After any environment change, record the variable names, not their values, and rerun health/readiness plus the relevant smoke tests.

## Migrations and seed

1. Take or confirm the approved database backup/restore point.
2. Verify the target project, environment label, connection mode, and `vector` extension.
3. Apply migrations in order using the direct migration connection where supported.
4. Verify schema and migration version without exporting content.
5. Seed only the approved disposable/demo tenant using `db/seed_demo.sql` or the application seed command.
6. Do not seed demo users/content into a client production-like tenant without explicit approval.
7. Start worker and indexing jobs only after database/search schema versions are compatible.
8. Record migration output, seed decision, and any `unverified` external checks.

The migration and seed files are present in this checkout, but database execution against Supabase or another target is `unverified` here. A reset operation must be explicitly scoped to a disposable database.

## Health checks, logging, and monitoring

Required API checks:

```powershell
Invoke-RestMethod https://api.example.invalid/health
Invoke-RestMethod https://api.example.invalid/health/ready
```

`/health` is liveness. `/health/ready` must report API, database/fixture, worker, connector, and index state without content, restricted existence hints, ACL payloads, embeddings, or secrets. Add web availability, worker heartbeat, queue lag, database connectivity, search/index health, and connector status to the target host’s checks.

Use structured, redacted logs with request/job ID, environment, release, route/job, duration, connector ID, runtime/capability label, retry category, and error code. Keep audit events separate. Never log query text, restricted excerpts, raw provider payloads, tokens, private keys, ACL bodies, or embeddings.

Agree before go-live on error tracking, alert thresholds, dashboard ownership, log retention, access review, incident response, and data redaction. These are not configured or live-verified by this handoff.

## Backups and restore

- Supabase: confirm the selected plan’s backups and point-in-time recovery behavior, retention, region, recovery permissions, and restore workflow.
- PostgreSQL/pgvector: verify schema, vector extension/version, migration artifacts, and seed/rebuild procedure after restore.
- OpenSearch: configure and test snapshots for managed or self-hosted deployments; record index version and rebuild path.
- Redis: decide whether persistence is required for the queue; durable product state must remain in PostgreSQL, not Redis alone.
- Secrets: back up/escrow rotation metadata through the approved secret manager; never back up raw secret values in repository artifacts.

Record restore-test date, owner, measured recovery scope, and any RPO/RTO decision. A backup setting or vendor feature is not restore evidence until the client performs a controlled test.

## Connector status handoff

Every connector card must expose its capability label (`fixture`, `live`, `blocked`, or `unverified`) separately from runtime status (`configured`, `running`, `healthy`, `degraded`, `failed`, or `paused`). Include last successful sync, current run, counts, freshness, categorized errors, checkpoints, and explicit capability gaps without returning raw credentials or restricted source content.

All eight source boundaries are listed in [CONNECTOR_MATRIX.md](CONNECTOR_MATRIX.md). Until live records exist, retain the fixture/unverified labels. A green fixture test does not establish live provider ACL fidelity.

## Rollback

Before rollout, record the release artifact, migration version, search-index version, queue schema, seed decision, and last known-good health/smoke evidence. On failure:

1. Pause new sync/index/evaluation work if it could worsen the state.
2. Roll back web/API/worker artifacts to the last verified compatible version.
3. Use only a pre-reviewed backward-compatible database rollback or approved restore.
4. Rebuild or select a compatible search index; never point an old binary at an incompatible schema without review.
5. Rotate/revoke affected credentials through the client secret manager if exposure is suspected.
6. Run health/readiness, permission-positive, permission-negative, preview, connector, and audit smoke tests.
7. Record outcome, data loss/replay scope, and remaining `unverified` checks.

No provider write-back action is part of this prototype. Any future write operation requires its own idempotency and rollback review before it is enabled.

## Go-live smoke tests

Run these after deployment and record exact output, environment, release, principal, and date:

```powershell
pytest tests/acceptance/test_documentation_contract.py -q
pytest -q
Set-Location apps/web
npm run lint
npm run build
Set-Location ../..
Invoke-RestMethod https://api.example.invalid/health
Invoke-RestMethod https://api.example.invalid/health/ready
```

Then manually verify, with approved seeded or client test data:

1. Allowed principal: canonical travel-policy query returns an answer with authorized citations from at least two sources when the seed supports it.
2. Denied principal: restricted content produces no-access-safe output and no restricted preview.
3. Preview recheck: stale, deleted, pending-recheck, changed-ACL, unknown-principal, and cross-tenant cases fail safely.
4. Admin: all eight connector cards expose capability/runtime labels, sync state, freshness, errors, and no secrets.
5. Worker: one safe sync/retry/failure path is observable without replaying an unsafe provider write.
6. Logs/audit: request/job IDs are traceable and content/secrets are absent.
7. Backup/restore: the approved controlled restore test has an owner/date/result.
8. Browser/DNS/TLS: the intended web origin reaches the intended API over HTTPS at the supported viewport sizes.

The current repository has local API/web contracts but cannot establish worker, connector, browser, provider, infrastructure, DNS/TLS, billing, backup-restore, or secret-manager evidence. Mark each such item `unverified` until client-owned live evidence exists; do not convert a missing check into a production claim.
