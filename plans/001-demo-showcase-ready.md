# Plan 001: Make the Knowledge demo API-backed and showcase-ready

> **Executor instructions**: Execute this plan step by step. For each production behavior, first write one focused test, run it and confirm the expected failure, make the smallest implementation, and rerun the test before starting the next behavior. Run every final gate. If a STOP condition occurs, stop and report rather than improvising. After independent review, update the status row in `plans/README.md`.
>
> **Drift check (run first)**: `git diff --stat 7ddea82..HEAD -- apps/api/main.py apps/api/config.py apps/api/services/answers.py apps/api/services/governance.py apps/web/app apps/web/components apps/web/lib apps/web/package.json apps/web/package-lock.json apps/web/playwright.config.ts apps/web/tests Dockerfile apps/web/Dockerfile docker-compose.yml .env.example README.md DEMO_SCRIPT.md RUNBOOK.md deployment.md tests plans`
>
> Work in an isolated worktree if available. For subagent execution, dispatch one implementer per numbered step, then independently review that step's diff and test evidence before dispatching the next implementer. Do not run two implementers concurrently in this repository.

## Status

- **Priority**: P1
- **Effort**: L
- **Risk**: MED
- **Depends on**: none
- **Category**: bug, tests, dx, docs, direction
- **Planned at**: commit `7ddea82`, 2026-08-19

## Why this matters

The repository has a strong fixture-backed FastAPI safety contract, but the browser currently renders a separate static story. An operator therefore cannot demonstrate that the browser actually receives server-authorized citations, safe denial, preview rechecks, connector state, or unanswered-query governance. This plan makes the UI consume the existing fixture API through a same-origin demo proxy, completes redacted unanswered administration, adds an easy fixture deployment path, and proves the full browser flow on API `8102` and web `3102`.

## Current state

- `apps/api/main.py:39-50` constructs `FixtureStore`, authorization, answer, preview, connector, governance, and evaluation services at process startup. It has typed routes for search/answer/preview at lines 107-122 and connector/admin routes at lines 142-190.
- `apps/api/config.py:9-36` defaults to `fixture`/`inline` providers, although the current application entrypoint has no PostgreSQL repository selection.
- `apps/api/services/answers.py:59-104` returns cited answered/refused/insufficient-context responses after authorization. `apps/api/services/governance.py:18-32` can persist a redacted unanswered record, but no source call invokes it; `/v1/admin/unanswered` at `apps/api/main.py:167-170` only reads the list.
- `apps/web/lib/api.ts:1-11` only defines `API_BASE_URL` and a request-shape helper; it has no request method and is not imported by the workbench.
- `apps/web/components/SearchWorkbench.tsx:142,167-198` renders `SEARCH_FIXTURE`, `ANSWER_FIXTURE`, and `PREVIEWS` imported from `components/types.ts`. `apps/web/components/ConnectorGrid.tsx:106-125` likewise renders and mutates `CONNECTOR_FIXTURES` locally.
- `tests/e2e/test_policy_trace.py:6-52` proves FastAPI allowed and denied behavior through `TestClient`; `tests/ui/test_routes_and_states.py:1-130` only checks source file presence/text. Neither opens a browser.
- `apps/web/package.json:5-23` contains development, build, and lint scripts but no browser-test command or direct browser-test dependency.
- `docker-compose.yml:1-40` starts only PostgreSQL, OpenSearch, and Redis. It contains no API/web service. `README.md:37-53` requires separate local processes and currently uses `npm install`; `README.md:95` says browser proof is still unverified.
- The product design at `docs/superpowers/specs/2026-08-09-permission-assistant-design.md:20-32` requires authorization before context construction and safe denial. The portfolio showcase spec requires a reproducible default fixture flow, health/readiness, build, desktop/mobile browser smoke, reset, and deploy guide.

Verified excerpts:

```tsx
// apps/web/components/SearchWorkbench.tsx:167-176
const [query, setQuery] = useState(SEARCH_FIXTURE.query);
const runSearch = (event: FormEvent<HTMLFormElement>) => {
  event.preventDefault();
  setRequestState("loading");
  setPhase("results");
};
```

```python
# apps/api/main.py:167-170
@app.get("/v1/admin/unanswered")
def unanswered(...):
    principal = require_admin(x_demo_principal)
    return governance.unanswered(principal)
```

```python
# apps/api/services/governance.py:18-32
def record_unanswered(self, query_id: str, category: str, safe_summary: str) -> UnansweredRecord:
    ...
    self._records.append(record)
    return record
```

Follow existing conventions: Pydantic contract field aliases are used by FastAPI; the fixture identity is an explicit demo principal resolved server-side; authorization must happen before retrieval/context; denied content must not appear in titles, snippets, scores, citations, preview output, or ordinary logs. The UI must retain the existing design tokens and accessible components from `apps/web/app/tokens.css` and `components/StatusBadge.tsx`. This is a fixture showcase only: its connector capability labels must remain `fixture`, `blocked`, or `unverified`, never `live`.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Python install | `python -m pip install -e ".[dev]"` | exit 0 |
| Focused API tests | `pytest tests/e2e/test_policy_trace.py tests/contracts/test_admin_routes.py -q` | focused tests pass |
| Full suite | `pytest -q` | all tests pass |
| Web install/lint/build | `npm --prefix apps/web ci; npm --prefix apps/web run lint; npm --prefix apps/web run build` | exit 0 |
| Fixture stack | `docker compose --profile fixture up --build -d` | API on 8102 and web on 3102 become healthy |
| Health checks | `Invoke-RestMethod http://localhost:8102/health; Invoke-RestMethod http://localhost:8102/health/ready` | fixture readiness is reported without source content |
| Browser smoke | `npm --prefix apps/web run test:showcase` | desktop and mobile primary-flow tests pass |
| Shutdown | `docker compose --profile fixture down` | exit 0 |

## Suggested executor toolkit

- Use `superpowers:test-driven-development` before each behavior change and retain red-test evidence in the implementation report.
- Use `superpowers:subagent-driven-development` for execution if a controller delegates this plan: one implementer and one independent reviewer per step.
- Use `superpowers:verification-before-completion` before commits, push/PR, or success claims.
- Read the workspace-root `docs/superpowers/specs/2026-08-19-six-demo-showcase-design.md` before Step 1; the ten showcase gates are binding.

## Scope

**In scope** (only these files may be modified or created):

- `apps/api/main.py`, `apps/api/config.py`, `apps/api/services/answers.py`, `apps/api/services/governance.py`
- `tests/e2e/test_policy_trace.py`, `tests/contracts/test_admin_routes.py`, `tests/evaluation/test_evaluation.py`, `tests/e2e/test_unanswered_governance.py` (new)
- `apps/web/app/api/backend/[...path]/route.ts` (new), `apps/web/app/api/demo-principal/route.ts` (new), `apps/web/app/page.tsx`, `apps/web/app/search/page.tsx`, `apps/web/app/admin/page.tsx`, `apps/web/components/SearchWorkbench.tsx`, `apps/web/components/ConnectorGrid.tsx`, `apps/web/components/AnswerPanel.tsx`, `apps/web/components/SourcePreview.tsx`, `apps/web/components/types.ts`, `apps/web/lib/api.ts`
- `apps/web/package.json`, `apps/web/package-lock.json`, `apps/web/playwright.config.ts` (new), `apps/web/tests/showcase.spec.ts` (new)
- `Dockerfile` (new), `apps/web/Dockerfile` (new), `docker-compose.yml`, `.env.example`, `README.md`, `DEMO_SCRIPT.md`, `RUNBOOK.md`, `deployment.md`, `plans/README.md`

**Out of scope**:

- Live Google Drive, SharePoint, Slack, Teams, Notion, Confluence, Jira, GitHub, model-provider, search-provider, database, queue, or worker integrations.
- PostgreSQL/OpenSearch repository implementation, database migrations, seed SQL changes, long-lived worker runner, enterprise authentication, production TLS/DNS, and real secrets.
- Any client-side authorization decision or passing an ACL decision from browser to API. A fixture identity selector is allowed only when the server proxy translates it into the existing fixture principal boundary.
- Root-workspace portfolio files, unrelated working-tree files, and Git metadata.

## Git workflow

- Branch: `feat/demo-showcase-ready`.
- Commit checkpoints: (1) `test(governance): characterize unanswered fixture records`; (2) `feat(api): record redacted unanswered outcomes`; (3) `feat(web): bind showcase to fixture API`; (4) `test(web): cover permission showcase flow`; (5) `docs(demo): add fixture deployment path`.
- Follow the observed conventional commits, for example `feat: add evidence-first client workbench` and `test: add acceptance and release verification`.
- Do not push or open a pull request without explicit operator authorization after every final gate is green. If authorized, push only `feat/demo-showcase-ready`, open a focused PR, and state that fixture tests do not prove live ACL/provider behavior.

## Steps

### Step 1: Specify redacted unanswered-query behavior at the API boundary

Create `tests/e2e/test_unanswered_governance.py` first. Add failing tests that:

1. submit an allowed fixture query with insufficient context, then as `admin-user` retrieve exactly one redacted unanswered record;
2. prove a denied/restricted request records only safe category/hash metadata and never restricted title, snippet, locator, or query text;
3. prove an answered canonical travel-policy request does not create an unanswered record; and
4. prove a non-admin cannot retrieve the aggregate.

Use `tests/e2e/test_policy_trace.py` and `tests/contracts/test_admin_routes.py` as patterns. Confirm failure because the governance service is not called by the answer/retrieval path.

**Verify (RED)**: `pytest tests/e2e/test_unanswered_governance.py -q` → fails because the expected record is absent, not because of a test setup/import error.

### Step 2: Record safe unanswered outcomes without weakening authorization

Add the smallest explicit integration between `AnswerService` and `GovernanceService` (constructor injection or a route-bound call) so only safe, redacted categories and a bounded summary enter governance. Keep original user text out of the record; never change the existing safe response shapes. Make the route return the existing typed answer before any UI work. Update `apps/api/main.py` wiring and tests only as needed.

Do not persist or display denied-content metadata. Maintain existing rule order: tenant/lifecycle/ACL filtering happens before answer context construction and before any governance summary is derived.

**Verify (GREEN)**: `pytest tests/e2e/test_unanswered_governance.py tests/e2e/test_policy_trace.py tests/contracts/test_admin_routes.py -q` → all pass, including safe-denial assertions.

### Step 3: Replace static browser fixtures with a same-origin server proxy

Before implementation, add focused source/API tests that fail because web requests do not occur. The browser contract must be:

- a fixture-only principal selector sets an HTTP-only/same-origin demo principal state through `app/api/demo-principal/route.ts`; it must accept only the known fixture principal keys and expose no credentials;
- `app/api/backend/[...path]/route.ts` reads that server-side state and forwards only the necessary `X-Demo-Principal` identity header to the configured API origin; it must return safe upstream errors and never forward provider credentials;
- `apps/web/lib/api.ts` owns typed request methods for search, answer, preview, connector status/sync history, evaluation, unanswered records, and audit;
- UI components render the returned API data rather than `SEARCH_FIXTURE`, `ANSWER_FIXTURE`, `PREVIEWS`, or `CONNECTOR_FIXTURES`.

Implement the smallest changes to the listed pages/components. Preserve their visible loading, fresh/stale, deleted, pending-recheck, unavailable, insufficient-context, refused, failed, no-accessible-context, fixture, blocked, and unverified states. The denied/cross-tenant UI path must display safe absence and no restricted content. Connector synchronization and evaluation must call fixture API routes and display their returned labels; do not retain timer-only state transitions.

Do not add FastAPI CORS as a workaround: the same-origin Next proxy is the required browser boundary. Do not expose a demo-principal header or a credential through public environment variables.

**Verify (RED then GREEN)**: run the new focused component/proxy tests first and confirm the static-fixture expectation fails; after implementation, run `pytest tests/ui tests/contracts tests/e2e -q` → all pass.

### Step 4: Add the browser showcase test before changing deployment documentation

Create `apps/web/playwright.config.ts`, add a direct browser-test dependency/script in `apps/web/package.json`, and update `package-lock.json` with the package manager. Write `apps/web/tests/showcase.spec.ts` before completing its UI behavior. It must run against API `8102` and web `3102` and cover:

1. allowed fixture principal: canonical query → authorized results → cited answer → safe preview;
2. denied and cross-tenant fixture principals: explicit safe absence with no restricted source hint;
3. admin fixture principal: all eight connector cards, fixture sync result, answered/unanswered administration, evaluation, and redacted audit surface;
4. desktop width `1280px` primary flow; and
5. mobile width `390px` with no horizontal overflow and keyboard-reachable primary controls.

The test must use the actual UI/API; it cannot assert hard-coded source strings that bypass the server. Ensure initial test failures identify missing runner, unavailable proxy, or missing behavior, then make only the minimal UI/proxy changes required to pass.

**Verify (RED then GREEN)**: `npm --prefix apps/web run test:showcase` → first fails for missing runner/behavior, then passes with both viewports.

### Step 5: Add a fixture-only deploy/reset path on the assigned ports

Before altering configuration, add/adjust a small smoke test that requires health/readiness to truthfully state fixture mode and that the web API proxy can reach it. Create a root `Dockerfile` for FastAPI and `apps/web/Dockerfile` for Next production runtime. Extend `docker-compose.yml` with a `fixture` profile that starts API and web as well as only necessary local dependencies, binds API `8102` and web `3102`, and avoids making PostgreSQL, OpenSearch, Redis, worker, or provider credentials prerequisites for the default scenario.

Keep fixture reset safe and repeatable: restarting the API rebuilds the in-memory store. Document that behavior; do not add a destructive database reset to the default fixture command. Update `apps/api/config.py`/health wording and `README.md`, `DEMO_SCRIPT.md`, `RUNBOOK.md`, and `deployment.md` so they no longer imply that the unimplemented PostgreSQL mode is a current runtime path. Use `npm ci` in documentation and Docker builds.

**Verify**: `docker compose --profile fixture up --build -d`; `Invoke-RestMethod http://localhost:8102/health`; `Invoke-RestMethod http://localhost:8102/health/ready`; `Invoke-WebRequest http://localhost:3102`; `docker compose --profile fixture restart api`; rerun the canonical browser smoke; `docker compose --profile fixture down` → all succeed and reset restores deterministic fixture behavior.

### Step 6: Complete repository verification and handoff

Run every command in **Done criteria** from a clean dependency environment. Confirm `git status --short` contains only in-scope files. Have an independent reviewer check that browser paths are API-backed, denied metadata cannot leak, and fixture-only deployment claims are accurate. Update `plans/README.md` after that review. Commit at the checkpoints above; push/open a PR only with explicit operator authorization.

**Verify**: retain exact output from every final command in the PR body when authorized.

## Test plan

- `tests/e2e/test_unanswered_governance.py`: answered vs insufficient-context vs denied outcomes, redaction, and admin authorization.
- Existing `tests/e2e/test_policy_trace.py`: regression coverage for allowed cited answer, safe preview, and denied response.
- Existing `tests/contracts/test_admin_routes.py` and `tests/evaluation/test_evaluation.py`: real fixture connector/evaluation administration.
- `apps/web/tests/showcase.spec.ts`: real browser API flow, allowed and denied identities, connector/evaluation/unanswered/audit admin surfaces, desktop/mobile layout and keyboard reachability.

## Done criteria

- [ ] The browser consumes FastAPI through a same-origin server proxy; no primary showcase response is rendered from static fixture constants.
- [ ] Fixture principal switching is server-mediated, accepts only known demo identities, and never sends an ACL decision or credential to the browser.
- [ ] Allowed flow returns API-backed cited answer and request-time preview; denied/cross-tenant flow reveals no restricted title, snippet, score, citation, locator, or existence signal.
- [ ] Unanswered records are generated only from safe outcomes, redact query/source content, are admin-only, and are visible in the real admin UI.
- [ ] API binds `8102`; web binds `3102`; explicit ports, startup, health, reset, verification, and shutdown are documented.
- [ ] `pytest -q` passes.
- [ ] `npm --prefix apps/web ci`, `npm --prefix apps/web run lint`, `npm --prefix apps/web run build`, and `npm --prefix apps/web run test:showcase` pass.
- [ ] Fixture Compose startup, health/readiness, web request, restart reset, browser smoke, and shutdown pass.
- [ ] No live connector/provider/durable-mode claim is introduced; all fixture boundaries retain honest labels.
- [ ] `git status --short` contains no out-of-scope file; `plans/README.md` status is updated after independent review.

## STOP conditions

- The drift check shows a material mismatch with any current-state excerpt.
- Implementing the proxy would require browser-side credentials, browser-supplied ACL decisions, or bypassing server-side authorization.
- A denied/cross-tenant browser smoke case exposes restricted metadata at any step.
- A database/OpenSearch/Redis/worker dependency becomes necessary for the default fixture Compose path.
- The assigned 8102/3102 ports conflict with a required showcase service and no approved port-map correction is supplied.
- A request requires implementing real PostgreSQL repositories, providers, or long-lived workers outside Scope.
- A verification fails twice after a reasonable scoped correction; stop and report the command/output.

## Maintenance notes

- Keep fixture identity simulation isolated to the same-origin demo proxy; production authentication must replace that boundary rather than inherit it.
- Reviewers should trace every browser action to a FastAPI route and ensure no component retains a static business-result fixture that can mask API drift.
- Keep governance records category/hash-only. Any request to show raw unanswered text, source titles, or denied metadata needs a separate privacy/security decision.
- Durable storage, live connector ACL fidelity, provider behavior, monitoring, backup/restore, and production deployment remain unverified after this showcase plan.
