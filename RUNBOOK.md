# Operational Runbook

This runbook covers the fixture demo and the handoff to a staging or production-like environment. It is an operating checklist, not evidence that infrastructure has been provisioned. The current checkout has a local API/web/fixture/database contract, but no worker runner, connector registry, or deployed infrastructure.

## Status vocabulary

Use two independent labels in every operational view:

| Label family | Values | Meaning |
|---|---|---|
| Connector capability | `fixture`, `live`, `blocked`, `unverified` | Whether the source integration has been proven in the target environment |
| Connector runtime | `configured`, `running`, `healthy`, `degraded`, `failed`, `paused` | Current observed sync/service state |
| Item lifecycle | `active`, `stale`, `deleted`, `pending_recheck` | Current source/index lifecycle state |

Never turn a fixture result into a live claim. `healthy` means the observed runtime check passed; it does not prove ACL fidelity, source coverage, or production readiness.

## Start and stop

### Local fixture demo

1. Confirm the checkout and selected database are disposable.
2. Activate the Python environment and install the project dependencies.
3. In fixture mode, reset by stopping/restarting the API process; its in-memory `FixtureStore` is rebuilt on process start. For PostgreSQL, use the migration/seed commands in [README.md](README.md) against a disposable database.
4. Start the API and web app from [README.md](README.md). Treat worker startup as `unverified` until a worker entrypoint and queue implementation exist.
5. Check `/health` and `/health/ready` before opening the demo.
6. Use only seeded principals and the canonical travel-policy question.
7. Stop the three processes when the demo ends and record any `unverified` checks.

Never improvise a destructive reset against a shared database. There is no `apps/api/cli.py` reset command in the current checkout.

### Staging or production-like environment

1. Confirm the environment label, release version, database target, search provider, queue provider, hostnames, and change owner.
2. Load secrets into the server-side secret manager; do not copy them into the web build or repository.
3. Apply migrations using a direct migration connection, then seed only an explicitly approved demo tenant if needed.
4. Start the worker before enabling connector sync or scheduled jobs.
5. Check API liveness/readiness, worker heartbeat, database, search, queue, and connector state.
6. Run the smoke tests in [deployment.md](deployment.md), with client-owned DNS, credentials, billing, and live checks recorded separately.

## Health checks and safe diagnostics

Run:

```powershell
Invoke-RestMethod https://api.example.invalid/health
Invoke-RestMethod https://api.example.invalid/health/ready
```

The hostname above is an example only; replace it only in a local command and do not commit a client hostname. Expected checks:

- `/health`: process liveness and version/build metadata that contains no secret or content.
- `/health/ready`: API, database/fixture, worker, connector, and index state; no source titles, excerpts, ACL payloads, embeddings, or credentials.
- Web: static asset availability and API-origin configuration.
- Worker: heartbeat, queue lease/lag, last successful job, and failure count.
- Database/search: connectivity and schema/index version, never a content dump.

If readiness fails, stop connector sync and investigate the dependency named in the redacted status. Do not bypass authorization or readiness to make a demo look healthy.

## Logging and monitoring

Log structured metadata: timestamp, environment, release, request/job ID, route or job name, principal/tenant identifier only when the identifier itself is approved, connector ID, capability label, runtime status, duration, retry classification, and redacted error code.

Do not log query text, restricted content, raw ACLs, embeddings, provider payloads, credentials, authorization tokens, private keys, or full source previews. Keep audit events separate from operational logs and apply the client-approved retention policy before enabling centralized collection.

Minimum monitoring to agree with the client:

- API error rate, latency, readiness failures, and safe-denial counts.
- Worker queue lag, lease expiry, retry counts, dead-letter/failure counts, and last successful sync.
- Search/index health and document/ACL propagation lag.
- Connector runtime status, last sync, item/error counts, and capability gaps.
- Database connections, storage, migration version, backup status, and restore-test date.

Alert thresholds, on-call routing, log retention, error tracking, and dashboards are client-owned and require live verification. No alerting system is provisioned by this documentation task.

## Connector triage

1. Confirm the capability label. A `fixture` or `unverified` card is not a provider outage.
2. Confirm runtime status, last successful sync, current run, checkpoint, item/error counts, and categorized error code.
3. Check provider status and scopes only with client-owned access; do not paste provider payloads into tickets.
4. Pause the affected connector if repeated failures could create stale or unsafe data. Keep other connectors isolated.
5. Retry only replay-safe reads/jobs according to the implementation contract. Do not transport-retry an ambiguous non-idempotent provider write; this prototype has no write-back actions.
6. Re-run a permission-positive and permission-negative check after recovery, then record the evidence location and remaining capability gaps.

## Lifecycle and permission incident response

If an item is stale, deleted, or pending recheck:

1. Preserve the request/job ID and lifecycle label.
2. Confirm request-time preview authorization and deletion/tombstone behavior.
3. Stop serving old content if current ACL or lifecycle state cannot be confirmed.
4. Reconcile the connector checkpoint/index job using an idempotent operation.
5. Verify that denied content did not enter answer context, preview output, browser state, or ordinary logs.

If possible permission leakage is reported, immediately pause the affected environment or connector, preserve redacted audit identifiers, revoke/rotate relevant credentials through the client’s secret manager, and run the no-leak tests before reopening access. Do not investigate by exporting restricted content.

## Fixture reset and data hygiene

Fixture reset is a process restart. For a disposable Docker PostgreSQL demo, the explicit reset is:

```powershell
docker compose down -v
docker compose up -d postgres
psql $env:DATABASE_URL -f db/migrations/001_initial.sql
psql $env:DATABASE_URL -f db/seed_demo.sql
```

Verify the database target, environment label, and backup posture first. `docker compose down -v` removes local volumes and is destructive. Never run it against a shared staging or production-like database. Production-like environments should use an approved migration and rollback plan, not demo seed data.

## Rollback

1. Declare the affected release, environment, owner, and user-visible symptom.
2. Disable new web/API traffic or pause workers/connectors as appropriate.
3. Roll back the application/web/worker artifact to the last verified version.
4. Apply only a pre-reviewed backward-compatible database migration rollback or restore; do not delete data from an unknown target.
5. Rebuild/reopen search indexes from the durable source only after schema and authorization versions are compatible.
6. Re-run health, permission-positive, permission-negative, preview, connector, and audit smoke tests.
7. Record whether rollback succeeded, what data/index versions were used, and which external checks remain `unverified`.

Database restore, OpenSearch snapshot restore, queue drain, DNS reversal, and credential rotation are deployment-owner actions described in [deployment.md](deployment.md). They are not claims that backups or rollback have been tested.

## Operator handoff checklist

- [ ] Environment and release IDs recorded.
- [ ] Client-owned credentials and provider scopes approved and stored server-side.
- [ ] Web/API/worker hosts, domains, TLS, and secret placement verified.
- [ ] Supabase/PostgreSQL/pgvector, search, and queue choices recorded.
- [ ] Migrations applied and approved seed decision recorded.
- [ ] Health/readiness, logs, monitoring, backups, and restore test status recorded.
- [ ] Eight connector capability labels and runtime statuses recorded.
- [ ] Smoke tests passed or explicitly marked `unverified` with owner/date.
- [ ] No secret values, restricted content, or unsupported production claims appear in the handoff evidence.
