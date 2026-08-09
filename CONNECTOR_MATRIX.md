# Connector Matrix

This matrix is the handoff boundary for the eight listed source systems. The default local label is `fixture`: it describes deterministic adapter/status behavior and is not a live provider connection. A connector may be labelled `live` only after a client-owned credential, required provider scopes, a successful sync, ACL checks, update/deletion checks, and a recorded verification run exist.

## Capability and runtime labels

Capability labels:

- `fixture`: deterministic local data or adapter behavior; no provider credential is implied.
- `live`: a target-environment provider connection has passed the agreed verification record.
- `blocked`: the connector cannot be exercised because credentials, scopes, network access, billing, or an explicit client decision is missing.
- `unverified`: the boundary is documented or implemented but live capability, ACL fidelity, or object coverage has not been proved.

Runtime statuses follow the product contract: `configured`, `running`, `healthy`, `degraded`, `failed`, and `paused`. These describe an observed connector run and must not be confused with the capability labels above.

## Source matrix

| Connector | Fixture/demo boundary | Live capability to verify | Client-owned inputs | Current handoff label |
|---|---|---|---|---|
| Google Drive | Documents, metadata, normalized ACLs, updates, deletions, and a preview locator | File-type coverage, inherited permissions, change feed, quota behavior, and deletion propagation | OAuth client, tenant consent, scopes, test folder, and billing/quota owner if applicable | `fixture`; live `unverified` |
| SharePoint | Pages/files or selected item types, metadata, normalized ACLs, updates, deletions, and preview locator | Site inheritance, Microsoft Graph/API scopes, delta behavior, list coverage, and tenant policy | App registration, tenant consent, scopes, selected sites, and test account | `fixture`; live `unverified` |
| Slack | Messages or selected channels, timestamps, channel-membership ACLs, updates, and deletion handling | Export/search scope, thread behavior, retention, app permissions, and channel membership fidelity | App installation, bot token, scopes, selected channels, and retention owner | `fixture`; live `unverified` |
| Teams | Messages from selected teams/channels, membership ACLs, timestamps, updates, and deletion handling | Message-history access, private channels, threads, retention, tenant policy, and Graph scopes | App registration, tenant consent, scopes, selected teams/channels, and test account | `fixture`; live `unverified` |
| Notion | Pages, blocks, parent metadata, page permissions, updates, and deletions | Block coverage, database rows, inherited shares, change notifications, and workspace restrictions | Integration token, workspace access, selected pages, and sharing policy | `fixture`; live `unverified` |
| Confluence | Pages, spaces, permissions, labels, updates, deletions, and preview locators | Space/page inheritance, attachments, pagination, account permissions, and deletion behavior | OAuth/API credential, site URL, scopes, selected spaces, and test account | `fixture`; live `unverified` |
| Jira | Issues, projects, selected fields/comments, issue/project permissions, updates, and deletions | Field visibility, issue security, comments, changelog behavior, pagination, and project scopes | OAuth/API credential, site URL, project allowlist, scopes, and test account | `fixture`; live `unverified` |
| GitHub | Repositories, issues/discussions or selected content, repository/team permissions, updates, and deletions | Organization policy, code/search scope, branch policy, token/app scopes, team mapping, and deletion behavior | App or token, installation scope, selected repositories, organization approval, and billing/policy owner | `fixture`; live `unverified` |

## Required verification record

Before changing a row from `fixture`, `blocked`, or `unverified` to `live`, record:

1. The tenant/workspace, connector configuration version, credential owner, and exact provider scopes.
2. Initial sync result, checkpoint, item counts, error count, and runtime status.
3. A permission-positive case and a permission-negative case, including a cross-tenant or out-of-scope item where applicable.
4. An update, deletion, ACL change, and retry/checkpoint case where the provider supports it.
5. Preview behavior, deep-link behavior, rate-limit behavior, unsupported object types, and the safe failure response.
6. Evidence location, test date, operator, and explicit gaps. A passing fixture test is not live evidence.

Connector credentials are accepted only by the secure API/worker boundary. They must never appear in browser responses, client logs, audit content, screenshots, or ordinary operational logs. The prototype has no provider write-back actions; sync, indexing, deletion reconciliation, and evaluation jobs must remain safe to replay according to their implementation contract.
