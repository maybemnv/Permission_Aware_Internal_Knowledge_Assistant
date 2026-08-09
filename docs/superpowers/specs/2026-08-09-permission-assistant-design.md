# Permission-Aware Internal Knowledge Assistant Design

## Scope and outcome

This implementation delivers the complete six-phase client-demo prototype described by `PRD.md` and `tasks.md`. It is a read-only, fixture-complete knowledge search and Q&A workbench with permission-safe retrieval, cited answers, source previews, content and ACL lifecycle handling, connector health, governance views, evaluations, and audit history.

The demo is deterministic on a clean checkout. Production-shaped boundaries remain explicit: Supabase is the preferred PostgreSQL/pgvector deployment target, search and worker providers are replaceable, model access is server-side, and all eight connectors expose honest fixture, blocked, or unverified capability states until live provider tests establish more.

## Architecture

The repository is a monorepo with four runtime boundaries:

- `apps/api`: FastAPI contracts, principal resolution, authorization, retrieval, answer generation, previews, connector/admin routes, and audit-safe error handling.
- `apps/web`: Next.js workbench for Search, Results, Answer, Source Preview, Connectors, Permissions, Unanswered, Evaluation, and Audit surfaces.
- `workers`: sync, normalization, ACL refresh, deletion reconciliation, indexing, and evaluation jobs behind a provider-neutral queue interface.
- `connectors`: common adapter protocol plus eight fixture/status adapters for Google Drive, SharePoint, Slack, Teams, Notion, Confluence, Jira, and GitHub.

`db/migrations` and `db/seed_demo.sql` define the durable tenant, principal, ACL, source, version, query, answer, citation, sync, feedback, evaluation, and audit state. The repository layer supports a deterministic fixture mode for local demos and a PostgreSQL/pgvector mode for deployment. Search retrieval is implemented behind a provider interface so lexical matching and metadata safety work in fixture mode while OpenSearch remains the production-like option.

The request path is:

1. Resolve the tenant and principal from the server-side demo identity.
2. Normalize the query and apply tenant/source/date/role/region filters.
3. Collect private lexical/vector candidates.
4. Evaluate every candidate with deny-by-default ACL and lifecycle policy.
5. Rerank and pack only authorized chunks.
6. Generate a context-only answer through the server-side model adapter.
7. Validate citations against the authorized, current evidence set.
8. Persist query, authorization, answer, citation, feedback, and audit events.
9. Recheck authorization for every preview and citation open.

Denied candidates never enter model context, client responses, embeddings exposed to clients, ordinary logs, analytics examples, or preview output. Unknown tenant, principal, ACL, lifecycle, connector, and freshness state denies access or returns a safe unavailable state.

## Persistence and contracts

The durable model contains tenant and principal identity, groups and role/region labels, connector and sync state, source items, independent content and ACL versions, normalized ACL subjects, content chunks, query and answer records, citations, feedback, evaluation runs/cases, and redacted audit events. Deleted items retain tombstones for reconciliation while content retrieval is disabled.

The API follows the PRD contracts:

- `POST /v1/search`
- `POST /v1/answers`
- `GET /v1/results/{resultId}/preview`
- `POST /v1/feedback`
- `GET /v1/connectors`
- `POST /v1/connectors/{connectorId}/sync`
- `GET /v1/connectors/{connectorId}/sync-runs`
- `GET /v1/admin/unanswered`
- `GET /v1/admin/evaluations`
- `POST /v1/admin/evaluations`
- `GET /v1/admin/audit`
- `GET /health`, `GET /health/ready`

All routes use typed Pydantic contracts and return the safe `ApiError` shape on failure. Admin routes require an administrator principal. Feedback, previews, connector status, audit, and evaluation responses contain only data authorized for the requesting principal.

## Fixture and connector strategy

The seed set contains one tenant with allowed, denied, unmapped, changed-group, cross-tenant, and administrator principals. It includes regional and role-based travel-policy content, an approval form, restricted-project content, independent content/ACL versions, a deleted item, a stale item, pending recheck state, and a categorized connector failure.

Each connector implements the shared identity/list/fetch/ACL/sync/checkpoint/preview contract. The eight adapters are fixture-backed by default and report status labels and capability gaps rather than pretending to authenticate to a provider. Sync operations are idempotent and classify retryable reads/jobs separately from non-replay-safe provider writes; this MVP has no provider write-back actions.

## UI design

The web workbench follows the shared `design.md` authority adapted to this product: warm neutral canvas, quiet technical density, 1px rules, restrained corners, Trebuchet MS display type, Segoe UI/Arial body type, monospace operational metadata, floating-pill navigation, stat strip, evidence-first search/review surface, supporting freshness and connector panels, no gradients or glass, visible focus, and reduced-motion support.

The main user journey is Search home → Results → Answer → Source Preview. The admin journey is Connector status → Permissions → Unanswered → Evaluation → Audit. Denial-safe absence is rendered as an explicit safe state without restricted titles, snippets, scores, citations, or existence hints. Loading, stale, deleted, pending recheck, unavailable, insufficient-context, refused, failed, and recoverable retry states are visible and do not rely on color alone. The layout must remain usable at 320px without horizontal overflow and support keyboard navigation and semantic labels.

## Testing and acceptance

Tests are organized by behavior: `tests/security`, `tests/retrieval`, `tests/connectors`, `tests/contracts`, `tests/lifecycle`, `tests/evaluation`, and `tests/ui`. The acceptance matrix maps every PRD Must requirement, task phase, and target to a reproducible check.

The critical test sequence is test-first for every new behavior: write a focused failing test, observe the expected failure, implement the smallest behavior, rerun the test, then run the relevant suite. Required coverage includes tenant isolation, unknown-deny behavior, pre-rerank filtering, no model leakage, citation validation, fresh preview checks, stale/deleted/ACL lifecycle changes, connector checkpoint/replay/failure handling, safe errors, admin redaction, accessibility, responsive rendering, and evaluation outcomes.

The prototype reports the PRD targets only when the local controlled test or evaluation run supplies evidence: zero permission leakage, at least 95% citation coverage, p95 search at or below 2.5 seconds in the controlled demo, at least 95% safe propagation within 15 minutes, and 8/8 connector status coverage. It will label provider ACL fidelity, model quality, retention, residency, compliance, and live connector parity as unverified unless tested.

## Go-live infrastructure direction

Supabase is the preferred production database option: use its managed PostgreSQL database and pgvector extension, private service credentials only in API/worker environments, pooled connections for web/API traffic, direct connections for migrations where supported, and database backups/PITR according to the selected plan. Row-level security may provide defense in depth, but the application authorization layer remains mandatory because the API must enforce the same policy before retrieval and model context construction.

Search has three reasonable deployment options:

1. Managed OpenSearch or Elasticsearch for production-like lexical/vector search and operational scaling.
2. A small self-hosted OpenSearch container for a prototype environment, with persistent storage and snapshots.
3. Supabase/PostgreSQL-only fixture or low-volume mode using PostgreSQL full-text search plus pgvector, accepting lower search scale and simpler operations.

Workers have two options:

1. Redis-backed queue with a separately deployed worker process for sync, indexing, deletion, and evaluations.
2. Supabase-backed job tables and scheduled invocations for a low-volume demo, with leases and idempotency keys implemented in application code.

The model provider is configurable between OpenAI and Claude through a server-side adapter. Connector credentials, model keys, database URLs, queue secrets, and admin tokens never reach the browser. A production deployment also needs a web host, API host, worker runtime, TLS/custom domain, centralized logs, error tracking, health checks, backups, secret rotation, and an operator-owned demo identity policy. These requirements are operational handoff content and belong in `deployment.md`, not in this design's implementation contracts.

## Explicit non-goals

This prototype does not add provider write-back actions, native mobile applications, anonymous/public search, enterprise SSO integration, foundation-model training, legal/compliance certification, guaranteed support for every provider object or ACL nuance, commercial pricing, scale, or SLA commitments.
