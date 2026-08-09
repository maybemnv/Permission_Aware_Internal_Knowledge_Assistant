# Permission-Aware Internal Knowledge Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete fixture-backed six-phase permission-aware search, cited Q&A, connector, lifecycle, governance, and client-demo prototype described by `PRD.md` and `tasks.md`.

**Architecture:** Use a FastAPI API with typed Pydantic contracts and a server-side deny-by-default policy over a deterministic fixture repository, with PostgreSQL/pgvector migrations and an adapter boundary for deployed persistence. Use a Next.js workbench for evidence-first search and governance surfaces, provider-neutral connector adapters and workers, and explicit fixture/live/blocked/unverified status labels.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic, pytest, SQLite fixture repository, PostgreSQL/pgvector SQL migrations, Next.js, React, TypeScript, CSS Modules, and Docker Compose-compatible service definitions.

## Global Constraints

- Preserve the PRD read-only MVP: no write-back actions, native mobile app, public access, SSO commitment, or compliance certification.
- Unknown tenant, principal, ACL, source, freshness, lifecycle, and connector state must deny or return a safe unavailable state without content or existence signals.
- Apply tenant and permission filtering before reranking, context packing, model access, citations, previews, analytics examples, and client responses.
- Recheck permission at every citation and source-preview open.
- Use explicit fixture identities, content/ACL versions, deletion tombstones, stale items, permission changes, and connector failures.
- Keep all eight connectors behind one contract and label fixture, live, blocked, and unverified capabilities honestly.
- Use the root `D:\ARC Automation Service\design.md` as visual authority adapted to evidence-first search; use shared tokens, visible focus, reduced motion, no gradients/glass, and no color-only state meaning.
- Every new behavior follows red-green-refactor: write a focused failing test, observe the expected failure, implement the smallest behavior, then rerun the focused and full suites.

---

### Task 1: Repository foundation, typed contracts, fixture schema, and acceptance matrix

**Files:**
- Create: `pyproject.toml`
- Create: `apps/api/__init__.py`, `apps/api/config.py`, `apps/api/domain/contracts.py`
- Create: `tests/contracts/test_contracts.py`
- Create: `tests/acceptance/acceptance_matrix.md`
- Create: `db/migrations/001_initial.sql`, `db/seed_demo.sql`
- Create: `.env.example`, `.gitignore`, `docker-compose.yml`
- Modify: `tasks.md` only to check off requirements when their implementation is verified

**Interfaces:**
- `apps.api.domain.contracts.SourceType`, `LifecycleState`, `AccessDecision`, `PrincipalContext`, `SearchRequest`, `SearchResponse`, `AnswerRequest`, `AnswerResponse`, `Citation`, `NormalizedSourceItem`, `SyncRun`, `SourceChangeEvent`, `AuditEvent`, and `ApiError` must mirror the PRD field names and enum values.
- `apps.api.config.Settings` must load fixture mode, database URL, search provider, queue provider, model provider, and server-side secret names from environment variables without exposing secret values.

- [ ] **Step 1: Write failing contract tests**

```python
def test_search_response_exposes_only_allowed_access_value():
    result = SearchResponse.model_validate({"queryId": "q", "results": [], "answerAvailable": False,
                                            "noAccessibleContext": True,
                                            "freshnessSummary": {"freshCount": 0, "staleCount": 0, "unknownCount": 0}})
    assert result.results == []
```

- [ ] **Step 2: Run `pytest tests/contracts/test_contracts.py -q` and confirm the missing-module/schema failure.**
- [ ] **Step 3: Implement the Pydantic contracts, settings loader, initial SQL schema, demo seed records, Compose service declarations, and environment template.** The SQL must include tenant scope, independent content/ACL versions, tombstones, vector column availability, audit fields, and unique `(connector_id, external_id)` identity.
- [ ] **Step 4: Rerun `pytest tests/contracts/test_contracts.py -q` and add validation for every PRD contract and safe error code.**
- [ ] **Step 5: Complete `tests/acceptance/acceptance_matrix.md` with one row per PRD Must requirement, each of the six phases, the no-leak targets, and an evidence column that starts as `not run` rather than claiming success.
- [ ] **Step 6: Commit with `git add pyproject.toml apps db tests .env.example .gitignore docker-compose.yml tasks.md` and `git commit -m "feat: establish typed prototype foundation"`.

### Task 2: Fixture repository and deny-by-default authorization spine

**Files:**
- Create: `apps/api/data/fixture_store.py`
- Create: `apps/api/security/authorization.py`
- Create: `apps/api/services/audit.py`
- Create: `tests/security/test_authorization.py`, `tests/security/test_no_leakage.py`

**Interfaces:**
- `FixtureStore.get_principal(principal_key: str) -> PrincipalContext | None`
- `FixtureStore.list_candidates(tenant_id: str, query: str, filters: SearchFilters) -> list[Candidate]`
- `FixtureStore.get_item(item_id: str) -> SourceItem | None`
- `FixtureStore.get_preview(item_id: str) -> SourcePreview | None`
- `FixtureStore.record(event: AuditEvent) -> None`
- `AuthorizationPolicy.evaluate(principal: PrincipalContext | None, item: SourceItem) -> AccessDecision`
- `AuthorizationPolicy.filter_authorized(principal, items) -> tuple[list[SourceItem], list[AuthorizationTrace]]`

- [ ] **Step 1: Write tests for allowed regional/role access, denied restricted access, unknown principal denial, cross-tenant denial, deleted/stale/pending-recheck handling, and the absence of title/snippet/score/item ID in denied outputs.**

```python
def test_unknown_acl_is_denied_without_an_existence_signal(store, policy, allowed_principal):
    item = store.item_with_acl_state("unknown-acl")
    assert policy.evaluate(allowed_principal, item) == AccessDecision.UNKNOWN
    assert policy.filter_authorized(allowed_principal, [item])[0] == []
```

- [ ] **Step 2: Run `pytest tests/security/test_authorization.py tests/security/test_no_leakage.py -q` and confirm failure caused by missing store/policy behavior.**
- [ ] **Step 3: Implement the in-memory fixture data with allowed, denied, unmapped, changed-group, cross-tenant, administrator, stale, deleted, and pending-recheck records. Implement audit persistence with actor, action, result, timestamp, correlation ID, and redacted metadata.
- [ ] **Step 4: Rerun the security tests and add assertions that denied text never reaches a model-context callback, ordinary log payload, or analytics record.**
- [ ] **Step 5: Commit with `git add apps/api/data apps/api/security apps/api/services tests/security` and `git commit -m "feat: add deny-by-default authorization spine"`.

### Task 3: Permission-filtered retrieval, cited answers, previews, and user API

**Files:**
- Create: `apps/api/services/retrieval.py`, `apps/api/services/answers.py`
- Create: `apps/api/routes/search.py`, `apps/api/routes/answers.py`, `apps/api/routes/previews.py`, `apps/api/routes/feedback.py`
- Create: `apps/api/main.py`
- Create: `tests/retrieval/test_pipeline.py`, `tests/retrieval/test_answers.py`, `tests/contracts/test_api_routes.py`

**Interfaces:**
- `RetrievalService.search(principal, request: SearchRequest) -> SearchResponse`
- `AnswerService.answer(principal, request: AnswerRequest) -> AnswerResponse`
- `AnswerService.validate_citations(answer_text, citations, authorized_items) -> list[Citation]`
- `PreviewService.open(principal, result_id: str) -> SourcePreview | ApiError`
- Routes must accept the demo principal from `X-Demo-Principal` server-side lookup; clients may not submit ACL decisions or model credentials.

- [ ] **Step 1: Write failing tests for exact/paraphrase/typo/source/date/role/region/no-result searches, pre-rerank permission filtering, two-source travel-policy answers, insufficient context, refusal, model failure, invalid citation, safe preview recheck, and safe feedback.**
- [ ] **Step 2: Run the focused retrieval/API tests and confirm expected missing-service failures.**
- [ ] **Step 3: Implement deterministic lexical scoring with tenant and metadata filtering, permission evaluation before sorting/context construction, bounded authorized context, a context-only deterministic model adapter, citation validation, answer states, and the safe `ApiError` contract.**
- [ ] **Step 4: Implement FastAPI dependency wiring and health/readiness endpoints. `/health/ready` must report API, fixture/database, worker, connector, and index state without content.
- [ ] **Step 5: Rerun focused tests, then `pytest tests/contracts tests/security tests/retrieval -q`.**
- [ ] **Step 6: Commit with `git add apps/api tests/contracts tests/retrieval` and `git commit -m "feat: implement permission-safe search and cited answers"`.

### Task 4: Connector contract, eight fixture adapters, sync workers, and categorized failures

**Files:**
- Create: `connectors/base.py`, `connectors/registry.py`, `connectors/adapters.py`
- Create: `workers/sync.py`, `workers/index.py`, `workers/evaluation.py`
- Create: `apps/api/routes/connectors.py`
- Create: `tests/connectors/test_adapter_contract.py`, `tests/connectors/test_sync_jobs.py`

**Interfaces:**
- `ConnectorAdapter.source_type`, `validate_configuration()`, `start_initial_sync()`, `start_incremental_sync()`, `fetch_item()`, `fetch_permissions()`, `resolve_preview()`, and `serialize_checkpoint()` must follow the PRD contract.
- `SyncCoordinator.start(connector_id: str, mode: SyncMode, idempotency_key: str) -> SyncRun`
- `SyncCoordinator.retry(sync_run_id: str) -> SyncRun`
- `ConnectorRegistry.statuses() -> list[ConnectorStatusSummary]`

- [ ] **Step 1: Write tests that instantiate all eight adapters, verify common methods, label fixture/blocked/unverified capabilities, reject duplicate running syncs, preserve checkpoints, handle duplicate events, isolate one failed connector, and replay only idempotent work.**
- [ ] **Step 2: Run connector tests and confirm the missing adapter/coordinator failures.**
- [ ] **Step 3: Implement the common adapter protocol, eight fixture adapters, status diagnostics, sync state machine, checkpoint handling, safe retry classification, quarantine, and worker indexing/deletion hooks.**
- [ ] **Step 4: Add admin connector routes and verify secrets are never returned in status or logs.**
- [ ] **Step 5: Rerun `pytest tests/connectors -q` and the full Python suite.**
- [ ] **Step 6: Commit with `git add connectors workers apps/api/routes/connectors.py tests/connectors` and `git commit -m "feat: add connector adapters and sync workers"`.

### Task 5: Content/ACL lifecycle, governance, evaluations, and admin API

**Files:**
- Create: `apps/api/services/lifecycle.py`, `apps/api/services/governance.py`, `apps/api/services/evaluation.py`
- Create: `apps/api/routes/admin.py`
- Create: `tests/lifecycle/test_versioning.py`, `tests/evaluation/test_evaluation.py`, `tests/security/test_admin_redaction.py`
- Modify: `apps/api/data/fixture_store.py`, `apps/api/main.py`

**Interfaces:**
- `LifecycleService.apply_change(event: SourceChangeEvent) -> LifecycleResult`
- `LifecycleService.recheck(item_id: str, principal: PrincipalContext) -> AccessDecision`
- `GovernanceService.unanswered(principal) -> list[UnansweredRecord]`
- `EvaluationService.run(dataset_version: str, principal_key: str | None) -> EvaluationRun`

- [ ] **Step 1: Write failing tests for content update, independent ACL change, group removal, deletion tombstone, stale propagation, pending recheck, failed old preview, unanswered categories, evaluation expected/actual permission outcomes, redacted admin examples, and audit filtering.**
- [ ] **Step 2: Run the lifecycle/evaluation/security tests and confirm missing behavior.**
- [ ] **Step 3: Implement independent content and ACL versions, tombstones, stale markers, query-time rechecks, redacted governance aggregations, evaluation cases, feedback categories, connector freshness counts, and filtered audit routes.**
- [ ] **Step 4: Add admin routes for `/v1/admin/unanswered`, `/v1/admin/evaluations`, `/v1/admin/audit`, and evaluation start; ensure non-admin users receive safe authorization errors.**
- [ ] **Step 5: Run `pytest tests/lifecycle tests/evaluation tests/security -q` and then the complete test suite.**
- [ ] **Step 6: Commit with `git add apps/api tests/lifecycle tests/evaluation tests/security` and `git commit -m "feat: add lifecycle governance and evaluation flows"`.

### Task 6: Next.js evidence-first workbench and accessibility states

**Files:**
- Create: `apps/web/package.json`, `apps/web/tsconfig.json`, `apps/web/next.config.mjs`
- Create: `apps/web/app/layout.tsx`, `apps/web/app/page.tsx`, `apps/web/app/tokens.css`
- Create: `apps/web/app/search/page.tsx`, `apps/web/app/admin/page.tsx`
- Create: `apps/web/components/SearchWorkbench.tsx`, `apps/web/components/AnswerPanel.tsx`, `apps/web/components/SourcePreview.tsx`, `apps/web/components/ConnectorGrid.tsx`, `apps/web/components/StatusBadge.tsx`
- Create: `tests/ui/test_routes_and_states.py`

**Interfaces:**
- The web client sends only typed requests to the API and uses `NEXT_PUBLIC_API_BASE_URL`; it never stores connector/model/database secrets.
- Components receive explicit `loading`, `stale`, `deleted`, `pending_recheck`, `unavailable`, `insufficient_context`, `refused`, and `failed` states and render text labels alongside color.

- [ ] **Step 1: Write UI contract tests that verify all required routes/components, design tokens, visible focus, reduced-motion media query, mobile overflow safeguards, and no restricted-content placeholder copy.**
- [ ] **Step 2: Run `pytest tests/ui/test_routes_and_states.py -q` and confirm missing files/tokens.**
- [ ] **Step 3: Implement the responsive workbench with floating-pill navigation, stat strip, search/filter rail, result rows, answer/citation flow, safe preview modal/panel, connector/admin panels, explicit empty/error/retry states, semantic labels, and keyboard interaction.**
- [ ] **Step 4: Run `npm install`, `npm run lint`, `npm run build`, and the UI contract tests. If a browser runner is unavailable, record browser verification as unverified rather than claiming it.**
- [ ] **Step 5: Commit with `git add apps/web tests/ui` and `git commit -m "feat: add evidence-first client workbench"`.

### Task 7: Client demo documentation, deployment handoff, and operational runbook

**Files:**
- Create: `README.md`, `DEMO_SCRIPT.md`, `RUNBOOK.md`, `CONNECTOR_MATRIX.md`, `deployment.md`
- Modify: `.env.example`, `tests/acceptance/acceptance_matrix.md`

**Interfaces:**
- `README.md` must provide clean-checkout setup, fixture seed/reset, API/web/worker commands, test commands, environment variable references, and known limitations.
- `deployment.md` must separate client-demo prototype, staging, and production-like options; document Supabase project/database setup, OpenSearch or Postgres-only search choice, worker/queue choice, web/API/worker hosting, custom domain/TLS, secret inventory without real secret values, `.env` placement, migrations/seed, health checks, logging/monitoring, backups, connector capability labels, rollback, and go-live smoke tests.

- [ ] **Step 1: Write documentation contract checks for required headings, all eight connectors, all secret names, no committed secret values, Supabase setup, provider options, and acceptance commands.**
- [ ] **Step 2: Run the doc checks and confirm missing-file failures.**
- [ ] **Step 3: Write the complete setup, demo, runbook, connector matrix, and deployment handoff. Include `[REDACTED_SECRET]` placeholders only and state which items require client-owned credentials, provider scopes, DNS, billing, or live verification.**
- [ ] **Step 4: Update acceptance evidence with commands actually run and explicit `unverified` entries for external provider/browser/infrastructure checks.**
- [ ] **Step 5: Rerun documentation checks and commit with `git add README.md DEMO_SCRIPT.md RUNBOOK.md CONNECTOR_MATRIX.md deployment.md .env.example tests/acceptance/acceptance_matrix.md` and `git commit -m "docs: add client demo and deployment handoff"`.

### Task 8: End-to-end verification, CI, and release evidence

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `tests/e2e/test_policy_trace.py`, `tests/test_release_artifacts.py`
- Modify: `tests/acceptance/acceptance_matrix.md`, `tasks.md`

- [ ] **Step 1: Write the end-to-end tests for the canonical allowed query, denied restricted query, citation preview recheck, admin connector/sync/failure path, lifecycle update/removal/deletion, and release artifact inventory.**
- [ ] **Step 2: Run the new tests and confirm they fail for missing integration wiring or unchecked task evidence.**
- [ ] **Step 3: Implement the smallest integration fixes and CI jobs for Python tests, API contract checks, web lint/build, documentation checks, and artifact safety.**
- [ ] **Step 4: Run the complete verification set from a clean-like state: `pytest -q`, `npm run lint`, `npm run build`, and a repository status/diff audit. Record exact pass counts, latency measurement scope, and unverified external items.**
- [ ] **Step 5: Check off only requirements backed by fresh evidence in `tasks.md` and the acceptance matrix.**
- [ ] **Step 6: Commit with `git add .github tests tasks.md` and `git commit -m "test: verify client demo acceptance flow"`.

### Task 9: Branch publication and master integration

**Files:**
- Modify: Git history only; do not overwrite unrelated user changes.

- [ ] **Step 1: Inspect `git status --short`, `git diff`, `git log --oneline`, and the complete verification output.**
- [ ] **Step 2: Push the focused branch to `origin` and create a concise PR with summary and testing evidence if the GitHub connector/CLI is available.**
- [ ] **Step 3: Merge or fast-forward the verified commit history to `master` only after the branch diff and checks are confirmed; push `master` to `origin`.**
- [ ] **Step 4: Verify `master` points to the published commit, the remote branch exists, and the worktree contains only intentionally untracked/generated files.**

## Self-review checklist

- Every PRD Must requirement maps to one plan task or the explicit non-goal boundary.
- No task depends on an undefined interface: contracts precede services, services precede routes, routes precede UI, and docs describe the implemented commands.
- Every production behavior has a failing test step before its implementation step.
- `deployment.md` is mandatory and includes Supabase plus alternative search/queue/hosting options without claiming live infrastructure.
- No plan step authorizes provider writes, secret commits, force-pushes, destructive resets, or unsupported production claims.
