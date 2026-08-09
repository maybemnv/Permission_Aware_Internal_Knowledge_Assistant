"""Deterministic, content-bearing demo repository used by fixture mode."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from apps.api.domain.contracts import (
    LifecycleState,
    PrincipalContext,
    SearchCandidate,
    SearchFilters,
    SourcePermission,
    SourceType,
)


DEMO_TENANT = "tenant-demo"
DEMO_INDEXED_AT = datetime(2026, 8, 9, 12, 0, tzinfo=timezone.utc)
SEARCH_STOP_WORDS = {"a", "an", "and", "are", "for", "my", "of", "the", "what", "with"}


class FixtureStore:
    """In-memory store whose records are intentionally explicit for rehearsals."""

    def __init__(self) -> None:
        self._principals = self._build_principals()
        self._items = self._build_items()

    def get_principal(self, principal_key: str) -> PrincipalContext | None:
        return self._principals.get(principal_key)

    def get_item(self, item_id: str) -> SearchCandidate | None:
        return self._items.get(item_id)

    def save_item(self, item: SearchCandidate) -> None:
        self._items[item.item_id] = item

    def list_candidates(
        self,
        tenant_id: str,
        query: str,
        filters: SearchFilters | None = None,
    ) -> list[SearchCandidate]:
        normalized_terms = [
            term for term in query.lower().split() if term and term not in SEARCH_STOP_WORDS
        ]
        candidates: list[SearchCandidate] = []
        for item in self._items.values():
            if item.tenant_id != tenant_id:
                continue
            if filters and filters.source_types and item.source_type not in filters.source_types:
                continue
            if filters and filters.updated_after and (
                item.source_updated_at is None or item.source_updated_at <= filters.updated_after
            ):
                continue
            if filters and filters.updated_before and (
                item.source_updated_at is None or item.source_updated_at >= filters.updated_before
            ):
                continue
            if filters and filters.role_labels and not set(filters.role_labels).intersection(item.role_labels):
                continue
            if filters and filters.region_labels and not set(filters.region_labels).intersection(item.region_labels):
                continue

            haystack = f"{item.title} {item.body}".lower()
            matched_terms = sum(term in haystack for term in normalized_terms)
            if normalized_terms and matched_terms == 0:
                continue
            candidates.append(item.model_copy(update={"score": float(matched_terms)}))

        candidates.sort(key=lambda item: (-item.score, item.item_id))
        return candidates

    def _build_principals(self) -> dict[str, PrincipalContext]:
        issued = DEMO_INDEXED_AT - timedelta(hours=1)
        return {
            "allowed-user": PrincipalContext(
                tenant_id=DEMO_TENANT,
                principal_id="principal-allowed",
                email="allowed@example.com",
                group_ids=["group-travel"],
                role_labels=["employee"],
                region_labels=["us-east"],
                auth_issued_at=issued,
            ),
            "denied-user": PrincipalContext(
                tenant_id=DEMO_TENANT,
                principal_id="principal-denied",
                email="denied@example.com",
                group_ids=["group-operations"],
                role_labels=["employee"],
                region_labels=["us-east"],
                auth_issued_at=issued,
            ),
            "unmapped-user": PrincipalContext(
                tenant_id=DEMO_TENANT,
                principal_id="principal-unmapped",
                email="unmapped@example.com",
                group_ids=[],
                role_labels=[],
                region_labels=[],
                auth_issued_at=issued,
            ),
            "changed-group-user": PrincipalContext(
                tenant_id=DEMO_TENANT,
                principal_id="principal-changed",
                email="changed@example.com",
                group_ids=["group-old"],
                role_labels=["employee"],
                region_labels=["us-east"],
                auth_issued_at=issued,
            ),
            "cross-tenant-user": PrincipalContext(
                tenant_id="tenant-other",
                principal_id="principal-cross-tenant",
                email="cross-tenant@example.com",
                group_ids=["group-travel"],
                role_labels=["employee"],
                region_labels=["us-east"],
                auth_issued_at=issued,
            ),
            "admin-user": PrincipalContext(
                tenant_id=DEMO_TENANT,
                principal_id="principal-admin",
                email="admin@example.com",
                group_ids=["group-admin"],
                role_labels=["administrator"],
                region_labels=["global"],
                auth_issued_at=issued,
                is_administrator=True,
            ),
        }

    def _build_items(self) -> dict[str, SearchCandidate]:
        updated = DEMO_INDEXED_AT - timedelta(days=2)
        stale_updated = DEMO_INDEXED_AT - timedelta(days=45)
        return {
            "item-travel-policy": self._item(
                item_id="item-travel-policy",
                source_type=SourceType.NOTION,
                title="Travel reimbursement policy",
                body=(
                    "Employees in us-east may claim economy travel and lodging with receipts. "
                    "Submit the travel approval form before booking and file reimbursement within 30 days."
                ),
                locator="notion://policies/travel-reimbursement#regional-rules",
                source_updated_at=updated,
                permissions=[SourcePermission(subject_type="group", subject_key="group-travel")],
                role_labels=["employee"],
                region_labels=["us-east"],
            ),
            "item-approval-form": self._item(
                item_id="item-approval-form",
                source_type=SourceType.GOOGLE_DRIVE,
                title="Travel approval form",
                body="Use the Travel Approval Form for manager approval, cost center, itinerary, and receipts.",
                locator="drive://forms/travel-approval",
                source_updated_at=updated,
                permissions=[SourcePermission(subject_type="group", subject_key="group-travel")],
                role_labels=["employee"],
                region_labels=["us-east"],
            ),
            "item-restricted-project": self._item(
                item_id="item-restricted-project",
                source_type=SourceType.GITHUB,
                title="Restricted project launch notes",
                body="Secret restricted project launch details must not be shown to ordinary employees.",
                locator="github://internal/restricted-project/launch.md",
                source_updated_at=updated,
                permissions=[SourcePermission(subject_type="group", subject_key="group-restricted-project")],
                role_labels=["engineering"],
                region_labels=["global"],
            ),
            "item-unknown-acl": self._item(
                item_id="item-unknown-acl",
                source_type=SourceType.SLACK,
                title="Unresolved source record",
                body="This content has an unknown ACL and must never be exposed.",
                locator="slack://unknown/record",
                source_updated_at=updated,
                permissions=[],
                acl_version="unknown",
            ),
            "item-deleted": self._item(
                item_id="item-deleted",
                source_type=SourceType.CONFLUENCE,
                title="Deleted travel FAQ",
                body="This tombstoned content is retained only for reconciliation.",
                locator="confluence://deleted/travel-faq",
                source_updated_at=updated,
                permissions=[SourcePermission(subject_type="group", subject_key="group-travel")],
                lifecycle_state=LifecycleState.DELETED,
            ),
            "item-pending-recheck": self._item(
                item_id="item-pending-recheck",
                source_type=SourceType.TEAMS,
                title="Pending permission record",
                body="This content awaits permission revalidation.",
                locator="teams://pending/recheck",
                source_updated_at=updated,
                permissions=[SourcePermission(subject_type="group", subject_key="group-travel")],
                lifecycle_state=LifecycleState.PENDING_RECHECK,
            ),
            "item-stale-policy": self._item(
                item_id="item-stale-policy",
                source_type=SourceType.SHAREPOINT,
                title="Legacy travel reimbursement policy",
                body="Legacy policy content is stale and should be checked against the current policy.",
                locator="sharepoint://policies/travel-legacy",
                source_updated_at=stale_updated,
                permissions=[SourcePermission(subject_type="group", subject_key="group-travel")],
                lifecycle_state=LifecycleState.STALE,
                indexed_at=stale_updated,
            ),
            "item-cross-tenant": self._item(
                item_id="item-cross-tenant",
                tenant_id="tenant-other",
                source_type=SourceType.JIRA,
                title="Other tenant project notes",
                body="This record belongs to another tenant.",
                locator="jira://other-tenant/project",
                source_updated_at=updated,
                permissions=[SourcePermission(subject_type="group", subject_key="group-travel")],
            ),
        }

    @staticmethod
    def _item(
        *,
        item_id: str,
        source_type: SourceType,
        title: str,
        body: str,
        locator: str,
        source_updated_at: datetime,
        permissions: list[SourcePermission],
        tenant_id: str = DEMO_TENANT,
        lifecycle_state: LifecycleState = LifecycleState.ACTIVE,
        acl_version: str = "v1",
        role_labels: list[str] | None = None,
        region_labels: list[str] | None = None,
        indexed_at: datetime = DEMO_INDEXED_AT,
    ) -> SearchCandidate:
        return SearchCandidate(
            item_id=item_id,
            tenant_id=tenant_id,
            source_type=source_type,
            title=title,
            body=body,
            locator=locator,
            source_updated_at=source_updated_at,
            indexed_at=indexed_at,
            lifecycle_state=lifecycle_state,
            acl_version=acl_version,
            acl_subjects=permissions,
            role_labels=role_labels or [],
            region_labels=region_labels or [],
            metadata={"content_hash": f"hash-{item_id}", "connector_id": f"connector-{source_type.value}"},
        )
