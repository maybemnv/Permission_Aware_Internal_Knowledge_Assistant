# Acceptance Matrix

This matrix maps the PRD Must requirements, the six implementation phases, and the numeric demo targets to reproducible evidence. `pass (local)` means the behavior is covered by the fixture/API test suite in this checkout. `unverified` means it requires a live provider, deployed infrastructure, browser, or controlled performance run.

## PRD Must requirements

| ID | Requirement | Evidence | Status |
|---|---|---|---|
| SRCH-01 | Natural-language query with source/date/role/region filters | `tests/retrieval/test_pipeline.py::test_source_and_date_filters_are_applied_before_authorization_output` | pass (local) |
| SRCH-02 | Lexical/vector retrieval boundary | `apps/api/services/retrieval.py`, `db/migrations/001_initial.sql`; live vector/search run | pass (local); live index unverified |
| SRCH-03 | Tenant and permission filtering during retrieval | `tests/retrieval/test_pipeline.py::test_search_filters_permissions_before_results_are_ranked` | pass (local) |
| SRCH-04 | Ranked safe result metadata | `tests/retrieval/test_pipeline.py::test_travel_search_returns_two_authorized_sources_with_stable_result_ids` | pass (local) |
| SRCH-05 | Denied metadata hidden | `tests/security/test_no_leakage.py` | pass (local) |
| SRCH-07 | No-access-safe state | `tests/retrieval/test_pipeline.py::test_search_filters_permissions_before_results_are_ranked`, `tests/e2e/test_policy_trace.py` | pass (local) |
| SRCH-08 | Stable result/citation identifier | `tests/retrieval/test_pipeline.py::test_travel_search_returns_two_authorized_sources_with_stable_result_ids` | pass (local) |
| QA-01 | Authorized context only | `tests/retrieval/test_pipeline.py::test_answer_uses_only_authorized_context_and_validated_citations` | pass (local) |
| QA-02 | Citation coverage or refusal | `tests/retrieval/test_pipeline.py::test_answer_uses_only_authorized_context_and_validated_citations`, `test_denied_question_returns_safe_refusal_without_model_call` | pass (local) |
| QA-03 | Insufficient context state | `apps/api/services/answers.py`, evaluation fixture | pass (local) |
| QA-04 | Citation source/freshness metadata | `tests/retrieval/test_pipeline.py`, `apps/api/domain/contracts.py` | pass (local) |
| QA-06 | Provider/hash boundary in answer contract | `db/migrations/001_initial.sql`, server-side model adapter | pass (local); live provider unverified |
| QA-07 | No browser model access | `tests/ui/test_routes_and_states.py::test_browser_bundle_does_not_handle_server_secrets` | pass (local) |
| QA-08 | Feedback contract | `apps/api/main.py`, `FeedbackRequest`, API route | pass (local) |
| PREV-01 | Fresh permission check | `tests/retrieval/test_pipeline.py::test_preview_rechecks_current_permission_and_returns_safe_error` | pass (local) |
| PREV-02 | Safe preview metadata | `apps/api/services/preview.py`, e2e policy trace | pass (local) |
| PREV-03 | Safe unavailable preview | `tests/e2e/test_policy_trace.py::test_denied_user_has_no_restricted_result_answer_or_preview_signal` | pass (local) |
| PREV-04 | Current/stale/deleted/pending state | `tests/lifecycle/test_versioning.py`, UI contract tests | pass (local) |
| PREV-05 | Preview is not an ACL bypass | security and e2e tests | pass (local) |
| CON-01 | Common interface for eight sources | `tests/connectors/test_adapter_contract.py::test_registry_exposes_all_eight_mvp_source_types` | pass (local) |
| CON-02 | Credentials outside web/API responses | `tests/connectors/test_adapter_contract.py::test_status_summaries_never_return_connector_credentials`, deployment handoff | pass (local); live secret manager unverified |
| CON-03 | Initial/incremental/deletion/checkpoint/retry boundary | `tests/connectors/test_sync_jobs.py`, `workers/sync.py` | pass (local) |
| CON-04 | Normalized opaque ACL subjects | `connectors/base.py`, adapter contract test | pass (local) |
| CON-05 | Connector status/count/freshness | `tests/contracts/test_admin_routes.py::test_admin_connector_status_covers_all_eight_sources` | pass (local) |
| CON-06 | Unsupported object types explicit | connector capability gaps and `CONNECTOR_MATRIX.md` | pass (local) |
| CON-07 | Failure isolation | `tests/connectors/test_sync_jobs.py::test_blocked_connector_failure_is_isolated_and_categorized` | pass (local) |
| GOV-01 | Query/retrieval/authorization/citation/feedback/sync/deletion events | `apps/api/services/audit.py`, audit-flow test, sync/lifecycle tests | pass (local) |
| GOV-02 | Unanswered categories | `tests/security/test_admin_redaction.py`, admin route | pass (local) |
| GOV-03 | Freshness and stale counts | retrieval response and connector statuses | pass (local) |
| GOV-04 | Evaluation run contract | `tests/evaluation/test_evaluation.py`, admin evaluation route | pass (local) |
| GOV-05 | Redacted analytics/admin data | `tests/security/test_admin_redaction.py`, admin route tests | pass (local) |

## Phase and demo gates

| Phase | Exit/demo gate | Evidence | Status |
|---|---|---|---|
| 0 | Fixture principals, contracts, readiness, no unauthorized content path | `tests/contracts`, `tests/security`, `db/seed_demo.sql`, `/health/ready` | pass (local) |
| 1 | Allowed/denied outputs and audit events | `tests/security`, `tests/contracts/test_api_routes.py`, audit flow | pass (local) |
| 2 | Two-source travel answer and restricted safe refusal | `tests/retrieval`, `tests/e2e/test_policy_trace.py` | pass (local) |
| 3 | Eight connector cards, sync progress/failure, safe retry | connector/admin tests and worker modules | pass (local) |
| 4 | Content/ACL update, permission removal, deletion, recheck | `tests/lifecycle/test_versioning.py`, preview tests | pass (local) |
| 5 | Governance/evaluation/audit UI and accessibility states | evaluation/admin/UI contract tests | pass (local); browser unverified |
| 6 | Demo script, runbook, connector matrix, deployment handoff | documentation contract tests and docs | pass (local); live rehearsal unverified |

## Numeric targets

| Target | Required evidence | Status |
|---|---|---|
| Zero permission leakage | Full no-leak suite plus controlled adversarial run | pass (local fixture); live provider leakage unverified |
| At least 95% citation coverage | Evaluation run reports `citation_coverage >= 0.95` | pass (local fixture) |
| p95 search at or below 2.5 seconds | Deployed controlled run with recorded environment and sample size | unverified |
| At least 95% safe propagation within 15 minutes | Deployed sync/update/delete propagation measurement | unverified |
| 8/8 connector status coverage | Connector registry/admin route returns eight sources | pass (local fixture); live integrations unverified |

## External verification boundary

Supabase project setup, pgvector extension execution, provider credentials/scopes, live ACL fidelity, OpenSearch/queue hosting, model-provider behavior, TLS/DNS, browser QA, backup/restore, monitoring, billing, retention, residency, compliance, and production scale are intentionally not claimed by local tests. `deployment.md` lists the owner, setup, secret, smoke-test, and rollback work required before a client go-live decision.
