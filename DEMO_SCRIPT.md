# Client Demo Script

## Purpose and guardrails

This is a 15–20 minute evidence-first walkthrough of the fixture-backed prototype. It demonstrates permission-safe retrieval, citations, freshness, lifecycle handling, connector status, and governance views. It does not demonstrate production ACL fidelity, live connector parity, model quality, scale, compliance, retention, residency, or an SLA.

Use only the seeded demo tenant and demo principals. Do not paste client content, provider tokens, private keys, or real personal data into the demo. Capability labels must remain `fixture`, `blocked`, or `unverified` unless a live verification record exists.

## Preflight

1. Start the fixture stack with `docker compose --profile fixture up --build -d` from [README.md](README.md). It binds FastAPI to `8102` and the web app to `3102`; no durable services or provider credentials are required.
2. Check `GET /health` and `GET /health/ready`. Confirm that readiness exposes service state only, not content, ACL payloads, embeddings, or secrets.
3. Confirm the selected principal is one of `allowed-user`, `denied-user`, `unmapped-user`, `changed-group-user`, `cross-tenant-user`, or `admin-user`, and that the UI is pointed at the intended API origin.
4. Open the connector/admin surface and note which cards are `fixture`, `blocked`, or `unverified`. Do not call a fixture card live.

## Walkthrough

### 1. Establish the question

Say:

> “We are going to ask a normal employee question, then follow the evidence all the way to a source preview. The important behavior is that authorization happens before reranking and answer context construction.”

Run:

> What is the travel reimbursement policy for my region and role?

Expected evidence:

- Search returns only sources authorized for the active principal and tenant.
- At least two authorized seeded sources are available if the fixture seed is complete.
- Results show source title, locator, connector, freshness, and citation affordances without leaking denied content.
- No permission decision is accepted from the browser; the server resolves `X-Demo-Principal`.

### 2. Inspect the cited answer

Open the answer view and say:

> “The answer is useful only to the extent that each material claim can be checked against the authorized evidence.”

Verify:

- The answer displays citations, freshness, caveats, and an explicit state such as supported, insufficient context, refused, or failed.
- Citations map to the authorized result set.
- Unsupported claims are caveated rather than filled with general model knowledge.
- A model key is never visible in the browser or ordinary logs.

### 3. Recheck source preview

Open a citation/source preview. Confirm that the preview repeats the authorization and lifecycle check at open time. The preview must show only an authorized current excerpt and its locator.

If the fixture changes the item to `stale`, `deleted`, or `pending_recheck`, rerun the preview. Expected behavior is a safe unavailable/stale state; the old content must not be presented as current evidence.

### 4. Demonstrate denial-safe behavior

Switch to a seeded restricted or unmapped principal, or use the planned denied fixture scenario. Ask for restricted-project material.

Say:

> “A denial is intentionally uninteresting. The user should not learn the restricted title, snippet, score, citation, or even an existence hint.”

Verify:

- The result is no accessible context, insufficient context, or another safe refusal state.
- No restricted content reaches the UI, answer context, analytics example, ordinary log, or preview.
- Cross-tenant and unknown-principal cases deny safely.

### 5. Show lifecycle and freshness

Open the governance or freshness surface. Walk through the seeded stale item, deleted item/tombstone, changed-group permission, and pending recheck state. Explain that request-time rechecks should deny early while background propagation completes.

Do not claim the `15 minute` propagation target is met unless a fresh controlled timing record exists. The target is an acceptance criterion, not an observed production SLA.

### 6. Show connector operations

Open connector administration and review all eight cards: Google Drive, SharePoint, Slack, Teams, Notion, Confluence, Jira, and GitHub.

Point out:

- Capability label: `fixture`, `live`, `blocked`, or `unverified`.
- Runtime status: `configured`, `running`, `healthy`, `degraded`, `failed`, or `paused`.
- Last sync, current run, item/error counts, freshness, and capability gaps when present.
- The seeded categorized failure is a fixture failure scenario, not evidence that a real provider is failing.

If a sync action exists, use only a fixture adapter or an explicitly approved test tenant. Never trigger an unverified provider write-back action; this prototype has none by design.

### 7. Close with governance

Show unanswered questions, evaluation results, and the redacted audit view. State:

> “The handoff makes evidence, freshness, permission boundaries, connector state, and gaps visible. Live scopes, DNS, billing, monitoring, backups, and restore behavior remain client-owned verification work.”

## If a step fails

Use [RUNBOOK.md](RUNBOOK.md) to classify the failure before changing data. Capture request ID, environment label, principal label, connector capability label, timestamp, and redacted error code. Do not capture source text or secrets in screenshots. If the failure is caused by an unavailable runtime or browser, record it as `unverified`; do not convert it into a pass claim.

## Post-demo reset

Fixture mode is in memory. Reset the default showcase without deleting data by restarting only the API:

```powershell
docker compose --profile fixture restart api
```

For a disposable PostgreSQL demo, reset only after confirming the database target:

```powershell
docker compose down -v
docker compose up -d postgres
psql $env:DATABASE_URL -f db/migrations/001_initial.sql
psql $env:DATABASE_URL -f db/seed_demo.sql
```

This removes local Docker volumes and is destructive. Never run it against a shared staging or production-like database. No application CLI reset entrypoint exists in the current checkout.
