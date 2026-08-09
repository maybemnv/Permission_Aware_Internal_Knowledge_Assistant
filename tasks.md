# Permission-Aware Internal Knowledge Assistant — Client Demo Prototype Tasks

**Goal:** Build a read-only internal search and Q&A prototype that returns cited, freshness-aware answers only from content the active principal is allowed to access, while making denied, stale, deleted, and connector-failure states auditable.

**Architecture:** Use Next.js for the search and governance workspace, FastAPI for typed APIs and authorization, PostgreSQL for tenant/principal/content/ACL/query/audit state, background workers for connector sync and indexing, and provider-neutral connector adapters. Permission filtering must happen before reranking and model context construction.

**Tech stack:** Next.js, FastAPI, PostgreSQL, worker queue, lexical/vector retrieval, and adapters for Google Drive, SharePoint, Slack, Teams, Notion, Confluence, Jira, and GitHub, as bounded by `PRD.md`.

## Global constraints

- [x] Preserve the PRD read-only MVP: no write-back actions, native mobile app, public access, SSO commitment, or compliance certification.
- [x] Enforce deny-by-default behavior. Unknown tenant, principal, ACL, source, freshness, or permission state must not leak content or existence signals.
- [x] Filter by tenant and permissions before reranking or constructing model context; recheck permission on every citation and source-preview open.
- [x] Use seeded fixture principals, documents, ACL changes, deletions, and connector failures for a repeatable client demo; label live, fixture, blocked, and unverified connectors.
- [x] Use `D:\ARC Automation Service\design.md` as the shared visual authority for quiet technical genre, workbench structure, palette, typography, spacing, shape, motion, focus, and explicit empty/error states. Adapt the content to evidence-first search; do not copy Revenue Recovery routes or metrics.
- [x] Do not claim production ACL fidelity, provider scopes, retention, residency, legal compliance, model quality, or connector parity until verified.

## Target file structure

- Create `apps/web/` for search, answer, source preview, admin, and governance routes.
- Create `apps/api/` for typed contracts, authorization, search/answer services, connector status, and audit queries.
- Create `workers/` for sync, normalization, ACL refresh, deletion reconciliation, indexing, and evaluation jobs.
- Create `db/migrations/` and `db/seed_demo.sql` for tenant, principal, ACL, source, chunk, query, answer, citation, sync, and audit state.
- Create `connectors/` for the common adapter contract and eight fixture/status adapters.
- Create `tests/security/`, `tests/retrieval/`, `tests/connectors/`, `tests/contracts/`, and `tests/ui/` for leakage, retrieval, sync, API, and interface coverage.
- Create `README.md`, `.env.example`, `DEMO_SCRIPT.md`, `RUNBOOK.md`, and `CONNECTOR_MATRIX.md` for repeatable operation.

## Phase 0 — Scope, fixtures, and safety contract

- [x] Convert every PRD Must requirement, the six build phases, and the evaluation targets into `tests/acceptance/acceptance_matrix.md`.
- [x] Record the greenfield status and choose reversible implementation boundaries for retrieval engine, queue, model provider, and fixture identities.
- [x] Define typed contracts for principal context, search request/response, answer request/response, citation, source preview, sync events, audit events, and safe `ApiError` responses.
- [x] Seed one tenant with regional/role principals: allowed user, denied user, unmapped principal, changed-group principal, cross-tenant principal, and administrator.
- [x] Seed authorized travel-policy and approval-form records plus restricted-project content with different ACLs, versions, and timestamps.
- [x] Add readiness checks that expose API, database, worker, connector, and index state without exposing content.

**Exit gate:** A clean checkout can start in fixture mode, all principals are explicit, and an unauthorized query has no path to content or existence metadata.

## Phase 1 — Safety spine and persistence

- [x] Scaffold the Next.js, FastAPI, database, worker, connector, and test boundaries from the PRD proposed directory tree.
- [x] Create tenant, principal, group, ACL, source item, chunk, content version, ACL version, query, answer, citation, sync job, and audit-event migrations.
- [x] Implement server-side workspace/tenant and principal authorization on every read, search, preview, connector, evaluation, and audit command.
- [x] Implement deny-by-default authorization for unknown, stale, deleted, cross-tenant, and pending-recheck records.
- [x] Persist audit events with actor, action, resource, result, timestamp, correlation ID, and redacted metadata.
- [x] Add no-leak tests for API responses, previews, citations, embeddings, model context, logs, error messages, and analytics.

**Demo gate:** Allowed and denied fixture principals receive the expected safe outputs and corresponding audit events.

## Phase 2 — Retrieval and cited Q&A

- [x] Implement lexical/vector retrieval with tenant filters, metadata filters, permission filtering before reranking, bounded context packing, and deterministic fixture ranking. (Vector search is deployment-provider unverified.)
- [x] Implement `/v1/search`, `/v1/answers`, source preview, feedback, health, and safe error contracts.
- [x] Implement answer states `answered`, `insufficient_context`, `refused`, `failed`, and `unavailable` with reason and retry/handoff guidance.
- [x] Validate every citation against the current authorized source version, source timestamp, and retrieved evidence span.
- [x] Build Search home, Search results, Answer, and Source preview views with freshness, source, permission-safe status, and feedback controls.
- [x] Add exact, paraphrase, typo, source/date-filter, no-result, insufficient-context, and prompt-injection fixture cases. (Prompt-injection live-model evaluation remains unverified.)

**Demo gate:** The question “What is the travel reimbursement policy for my region and role?” returns a cited answer from at least two authorized seeded sources; restricted content returns no-access-safe output.

## Phase 3 — Connector framework and sync

- [x] Implement the common adapter contract for identity, source listing, item fetch, content normalization, ACL normalization, initial sync, incremental sync, deletion, and checkpointing.
- [x] Provide fixture/status adapters for Google Drive, SharePoint, Slack, Teams, Notion, Confluence, Jira, and GitHub without pretending all provider operations are live.
- [x] Implement credential isolation, sanitized logs, sync job state, retry classification, categorized terminal failures, quarantine, and operator replay.
- [x] Expose connector health, last sync, item counts, freshness, current ACL state, error reason, capability gaps, and live/fixture/blocked status.
- [x] Prove at least two-source seeded retrieval and one categorized connector failure in the admin workspace.
- [x] Add normalization, checkpoint, duplicate event, partial failure, and replay contract tests.

**Demo gate:** An administrator starts a sync, observes progress and failure state, retries safely, and searches current authorized content without seeing provider secrets.

## Phase 4 — Content and permission lifecycle

- [x] Implement independent content and ACL versions, update detection, tombstones, permission-change events, stale markers, and deletion reconciliation.
- [x] Recheck permission at query time, citation open, source preview open, and admin action time; never rely only on indexed ACL state.
- [x] Remove deleted or newly unauthorized content from search results, citations, embeddings, model context, previews, and analytics views.
- [x] Show fresh, stale, deleted, and pending-recheck states with text and accessible status; hide restricted existence rather than blurring it.
- [x] Add lifecycle fixtures for content update, permission removal, group change, deletion, delayed sync, and failed old-preview access.

**Demo gate:** Updated content becomes current, removed access denies at request time, and deleted content disappears from search and citations.

## Phase 5 — Governance, evaluation, and UI

- [x] Implement feedback, unanswered-question categories, stale-item counts, redacted analytics, evaluation runs, and filtered audit history.
- [x] Build Permissions, Unanswered, Evaluation, and Audit screens alongside connector health and sync inspection.
- [x] Apply the root `design.md` schema: modern-minimal quiet technical workbench, stat strip for operational counts, search/review surface, evidence/freshness supporting panels, floating-pill navigation, and inline-rule footer.
- [x] Use the shared brand tokens, Trebuchet MS display, Segoe UI/Arial body, Consolas or `ui-monospace` data, 4-point spacing, 1px rules, restrained corners, no gradients/glass, visible focus, and reduced motion.
- [x] Map the product information architecture to Search home, Results, Answer, Source preview, Permissions, Unanswered, Evaluation, Audit, and Connector status routes. (Admin surfaces are fixture-backed in the current web route.)
- [x] Show source, freshness, citation, permission-safe state, denial-safe state, loading, stale, deleted, unavailable, and recoverable error states without color-only meaning.
- [ ] Verify keyboard navigation, visible focus, screen-reader labels, responsive layout at the PRD target width, honest skeleton loading, and no horizontal overflow. (Static UI contracts pass; browser QA remains unverified.)

**Exit gate:** A client can follow evidence from query to citation and understand freshness, connector state, permissions, and evaluation limits without reading logs.

## Phase 6 — Demo rehearsal and client handoff

- [ ] Rehearse the allowed-user query with two cited sources, freshness, approval-form evidence, and source preview. (Automated e2e passes; live client rehearsal remains unverified.)
- [x] Switch to a principal outside the restricted-project group and demonstrate no title, snippet, score, citation, or existence signal plus the denial audit event.
- [x] As administrator, show eight connector cards, one sync run, one categorized failure, unanswered questions, evaluation results, and audit history in fixture mode.
- [x] Trigger content update, permission removal, and deletion fixtures; show stale/deleted handling and failed old preview access in automated lifecycle/preview tests.
- [x] Run contract, no-leak, retrieval, connector, lifecycle, evaluation, accessibility, responsive, and failure-recovery tests. (Browser/responsive runtime remains unverified.)
- [ ] Measure the PRD targets: zero permission leakage, at least 95% citation coverage, p95 search at or below 2.5 seconds in the controlled demo, at least 95% safe propagation within 15 minutes, and 8/8 connector status coverage. (Local fixture reports citation and 8/8 status; p95/propagation/live leakage remain unverified.)
- [x] Add `README.md` with setup, fixture seed/reset, demo mode, tests, environment variables, and known limitations.
- [x] Add `DEMO_SCRIPT.md` with exact accounts, questions, expected safe outputs, provider labels, and fallback steps.
- [x] Add `RUNBOOK.md` with secret handling, sync/retry/quarantine operations, deletion procedure, ACL incident response, audit interpretation, and client-owned configuration.
- [x] Add `CONNECTOR_MATRIX.md` identifying live, fixture, restricted, blocked, and unverified behavior for every listed source.
- [x] Deliver an acceptance report mapping every PRD Must requirement to pass, explicit deferral, or blocker.

## Canonical client demo

1. Sign in as the allowed regional/role-based fixture.
2. Ask, “What is the travel reimbursement policy for my region and role?”
3. Show ranked evidence from two seeded sources, cited answer text, freshness, and approval-form citation.
4. Open a citation and demonstrate the fresh permission check and safe source preview.
5. Switch to an unauthorized principal and show no restricted title, snippet, score, citation, or existence signal.
6. Open the denial audit event as an administrator.
7. Show connector cards, sync progress, one categorized failure, unanswered questions, evaluation results, and audit history.
8. Trigger update, permission removal, and deletion fixtures and demonstrate stale/deleted behavior.
9. Label each surface as live, fixture-backed, blocked, or intentionally unsupported.

## Final acceptance gates

- [x] The allowed-user answer is cited, freshness-aware, and reproducible from seeded data.
- [x] Unauthorized content cannot appear in results, previews, citations, embeddings, model context, logs, or analytics.
- [x] Content and ACL lifecycle changes are visible, recoverable, and safe.
- [x] Connector capabilities and failures are honest and operator-visible.
- [ ] The UI follows the shared `design.md` schema with explicit states and responsive/accessibility coverage. (Static contracts/build pass; browser QA remains unverified.)
- [x] The README, demo script, runbook, connector matrix, and acceptance report make the prototype usable for client fine-tuning.
