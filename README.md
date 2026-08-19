# Permission-Aware Internal Knowledge Assistant

This repository describes a read-only, permission-aware internal search and Q&A prototype. The intended demo is deterministic and fixture-backed: an allowed principal can find a cited travel-policy answer, while denied, stale, deleted, cross-tenant, and connector-failure states remain safe and visible.

This checkout contains the product requirements, implementation plan, design handoff, a fixture-backed FastAPI/web prototype, connector registry/worker modules, database migration/seed artifacts, and contract/security/retrieval/UI tests. A long-lived queue worker process is not provisioned locally; commands below separate available interfaces from `unverified` deployment checks.

## Quick start

Use a disposable checkout and a local Python environment. PowerShell examples are shown because this project is maintained on Windows.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Copy `.env.example` to `.env` and fill only the values required for the selected local mode. The current template uses fixture/inline defaults and empty secret values. Never commit `.env`, provider credentials, connector exports, or private keys.

The fixture mode is the default demo boundary. It must not be presented as proof of provider ACL fidelity, production performance, retention, residency, compliance, or connector parity.

## Fixture showcase stack

The default showcase has no PostgreSQL, OpenSearch, Redis, worker, provider credential, or browser-visible API credential prerequisite. From the repository root, run:

```powershell
docker compose --profile fixture up --build -d
Invoke-RestMethod http://localhost:8102/health
Invoke-RestMethod http://localhost:8102/health/ready
Invoke-WebRequest http://localhost:3102
```

Open `http://localhost:3102`, select a fixture principal, and use the canonical travel question. The browser calls FastAPI only through its same-origin server proxy; `API_ORIGIN` is server-only. Restarting the API is the safe fixture reset because it recreates the in-memory store:

```powershell
docker compose --profile fixture restart api
npm --prefix apps/web run test:showcase
docker compose --profile fixture down
```

## Fixture seed and reset

Fixture mode is in memory: restarting the API process recreates `FixtureStore` and its deterministic records. For a disposable PostgreSQL run, apply the migration and seed files in order:

```powershell
docker compose up -d postgres
psql $env:DATABASE_URL -f db/migrations/001_initial.sql
psql $env:DATABASE_URL -f db/seed_demo.sql
```

For a local-only database reset, first verify the target is disposable, then use `docker compose down -v` followed by the commands above. This removes local Docker volumes and must never be run against a shared or production-like database. There is no `apps/api/cli.py` reset command in the current checkout; do not document or invoke one as if it were available.

A deployment owner must still verify that migrations are forward-compatible, that `vector` is enabled before vector columns are created, and that the seed is restricted to a demo tenant and demo principals.

The current fixture set includes regional and role-based travel policy, an approval form, restricted content, changed permissions, stale and deleted items, a pending recheck, a cross-tenant item, and explicit unknown-ACL data. The eight connector statuses and one categorized failure are defined by the fixture registry and SQL seed; live connector execution remains unverified.

## Run the API, web, and worker

Run each boundary in a separate terminal after the implementation files and dependencies are available:

```powershell
# API; FastAPI entrypoint is present; endpoint execution still requires a live process check
python -m uvicorn apps.api.main:app --reload --port 8102

# Web; package scripts are present; dependency install/build/browser checks remain unverified
Set-Location apps/web
npm ci
npm run dev -- --port 3102

# Worker coordinator/index modules; a long-lived queue runner is deployment-specific
Set-Location ../..
python -c "from connectors.registry import ConnectorRegistry; from workers.sync import SyncCoordinator; print(SyncCoordinator(ConnectorRegistry.demo()).start('connector-google_drive', 'initial', 'readme-demo').status)"
```

The web client may receive only the non-secret `NEXT_PUBLIC_API_BASE_URL`. Database URLs, model keys, queue credentials, connector credentials, and admin tokens belong only to server-side API, worker, migration, or secret-manager contexts.

Check the API without exposing content:

```powershell
Invoke-RestMethod http://localhost:8102/health
Invoke-RestMethod http://localhost:8102/health/ready
```

`/health` is liveness. `/health/ready` is readiness and should summarize API, database/fixture, worker, connector, and index state without titles, excerpts, ACL payloads, embeddings, or secrets.

## Demo identity and canonical query

The API resolves the demo principal server-side from `X-Demo-Principal`; clients do not submit ACL decisions. Use the fixture keys `allowed-user`, `denied-user`, `unmapped-user`, `changed-group-user`, `cross-tenant-user`, and `admin-user` supplied by `FixtureStore`. Their corresponding emails are display data, not request keys.

Canonical question:

> What is the travel reimbursement policy for my region and role?

The acceptance path is Search → Results → Answer → Source Preview. The answer is acceptable only when its citations are drawn from authorized, current evidence. A restricted question should return a safe no-access or insufficient-context state without restricted titles, snippets, scores, citations, or existence hints. The full talk track is in [DEMO_SCRIPT.md](DEMO_SCRIPT.md).

## Tests and acceptance commands

Run the documentation contract first:

```powershell
pytest tests/acceptance/test_documentation_contract.py -q
```

The implementation verification set is:

```powershell
pytest tests/contracts tests/security tests/retrieval -q
pytest -q
Set-Location apps/web
npm run lint
npm run build
npm run test:showcase
Set-Location ../..
```

The focused documentation contract passes locally. Fresh full-suite counts and web build evidence are recorded during final verification; provider, browser, external infrastructure, DNS, TLS, billing, secret-manager, and backup-restore checks remain `unverified` until performed in their target environment. Record exact output and scope before marking an acceptance item as passed.

## Environment variables

Use the smallest set for the chosen mode. The names below are the handoff contract, not proof that every adapter or provider is wired in this checkout.

| Variable | Placement | Purpose | Secret? |
|---|---|---|---|
| `APP_ENV` | API/worker | `demo`, `staging`, or `production-like` operating label | No |
| `APP_MODE` | API/worker | `fixture` or `postgres`; enables deterministic fixture behavior by default | No |
| `DEMO_PRINCIPAL` | API/worker | Default fixture principal key, `allowed-user` | No |
| `API_HOST` / `API_PORT` | API | Bind address and port | No |
| `DATABASE_URL` | API/worker/migration | PostgreSQL connection string; use pooled runtime and direct migration connections where supported | Yes |
| `SUPABASE_POOLER_URL` / `SUPABASE_DIRECT_URL` | API/worker/migration | Optional Supabase pooled/direct connection split | Yes |
| `DB_SSL_MODE` | API/worker/migration | Database TLS mode, default `require` in the local template | No |
| `SEARCH_PROVIDER` | API/worker | `fixture`, `postgres`, or `opensearch` | No |
| `OPENSEARCH_URL` | API/worker | Search endpoint when OpenSearch is selected | No, unless embedded credentials are used; never embed them |
| `OPENSEARCH_INDEX` | API/worker | Index name and version namespace | No |
| `OPENSEARCH_USERNAME` | API/worker | Search service identity, if required | No |
| `OPENSEARCH_PASSWORD` | API/worker/secret manager | Search service password | Yes |
| `QUEUE_PROVIDER` | API/worker | `inline`, `redis`, or `supabase_jobs` | No |
| `REDIS_URL` | API/worker | Redis queue endpoint when Redis is selected | Yes |
| `MODEL_PROVIDER` | API/worker | `deterministic`, `openai`, or `anthropic` | No |
| `OPENAI_API_KEY` | API/worker/secret manager | Server-side OpenAI model credential, if selected | Yes |
| `ANTHROPIC_API_KEY` | API/worker/secret manager | Server-side Anthropic model credential, if selected | Yes |
| `MODEL_NAME` | API/worker | Model identifier when a live model adapter is selected | No |
| `APP_SECRET_KEY` | API/worker/secret manager | Application signing/encryption secret if the selected deployment uses it | Yes |
| `ADMIN_PRINCIPAL_KEYS` | API/worker | Comma-separated approved admin fixture/identity keys | Sensitive identifier; not a credential |
| `AUDIT_RETENTION_DAYS` | API/worker | Optional audit retention setting | No |
| `ADMIN_TOKEN` | API/secret manager | Temporary operator/admin control, if the selected deployment uses one | Yes |
| `CONNECTOR_CREDENTIALS_ENCRYPTION_KEY` | API/worker/secret manager | Encryption boundary for connector credentials at rest | Yes |
| `NEXT_PUBLIC_API_BASE_URL` | Web build/runtime | Browser-visible API origin; it must contain no credentials | No |

Connector-specific names are listed in [deployment.md](deployment.md). They are client-owned inputs and should remain unset in fixture mode. Put server-side values in the host secret manager or local `.env`; do not put them in `NEXT_PUBLIC_*` variables, browser bundles, source control, ordinary logs, or screenshots.

## Known limitations

- The local FastAPI, fixture store, migration, seed, web package, connector registry, and worker modules are present. A long-lived queue worker process remains deployment-specific.
- Live provider execution, browser QA, performance, and external infrastructure remain unverified even when fixture tests pass.
- All eight connector boundaries are fixture-backed or status-only by design until live provider tests establish scopes, object coverage, change feeds, deletion behavior, and ACL fidelity. See [CONNECTOR_MATRIX.md](CONNECTOR_MATRIX.md).
- A fixture result does not demonstrate production authorization correctness. Application authorization must remain mandatory even if Supabase Row Level Security is later added as defense in depth.
- Search may use managed OpenSearch, self-hosted OpenSearch, or PostgreSQL full-text search plus pgvector. Scale, relevance, latency, and operating cost are not verified across those options.
- Redis and Supabase-backed job tables are alternatives; no queue, worker host, retry policy, or scheduler is provisioned by this documentation handoff.
- The prototype has no provider write-back actions, anonymous/public search, enterprise SSO integration, compliance certification, retention/residency commitment, SLA, or guaranteed support for every provider object and ACL nuance.
- Client-owned credentials, provider scopes, billing, DNS, TLS certificates, secret rotation, monitoring, backups, restore tests, and live browser/infrastructure verification are required before any production-like claim.

Operational procedures are in [RUNBOOK.md](RUNBOOK.md), the scripted review is in [DEMO_SCRIPT.md](DEMO_SCRIPT.md), and deployment choices are in [deployment.md](deployment.md).
