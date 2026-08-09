"""Deny-by-default policy applied before ranking, context construction, or preview."""

from __future__ import annotations

from dataclasses import dataclass

from apps.api.domain.contracts import (
    AccessDecision,
    LifecycleState,
    PrincipalContext,
    SearchCandidate,
)


@dataclass(frozen=True)
class AuthorizationTrace:
    """Redacted decision evidence safe for audit storage."""

    item_id: str
    decision: AccessDecision
    reason_code: str


class AuthorizationPolicy:
    def __init__(self, *, allow_stale: bool = True) -> None:
        self.allow_stale = allow_stale

    def evaluate(
        self,
        principal: PrincipalContext | None,
        item: SearchCandidate,
    ) -> AccessDecision:
        if principal is None:
            return AccessDecision.UNKNOWN
        if principal.tenant_id != item.tenant_id:
            return AccessDecision.DENY
        if item.lifecycle_state is LifecycleState.DELETED:
            return AccessDecision.DENY
        if item.lifecycle_state is LifecycleState.PENDING_RECHECK:
            return AccessDecision.DENY
        if item.lifecycle_state is LifecycleState.STALE and not self.allow_stale:
            return AccessDecision.DENY
        if item.acl_version == "unknown" or not item.acl_subjects:
            return AccessDecision.UNKNOWN
        if principal.is_administrator:
            return AccessDecision.ALLOW

        for subject in item.acl_subjects:
            if subject.subject_type.value == "principal" and subject.subject_key in {
                principal.principal_id,
                principal.email,
            }:
                return AccessDecision.ALLOW
            if subject.subject_type.value == "group" and subject.subject_key in principal.group_ids:
                return AccessDecision.ALLOW
            if subject.subject_type.value == "role" and subject.subject_key in principal.role_labels:
                return AccessDecision.ALLOW
        return AccessDecision.DENY

    def filter_authorized(
        self,
        principal: PrincipalContext | None,
        items: list[SearchCandidate],
    ) -> tuple[list[SearchCandidate], list[AuthorizationTrace]]:
        authorized: list[SearchCandidate] = []
        traces: list[AuthorizationTrace] = []
        for item in items:
            decision = self.evaluate(principal, item)
            traces.append(
                AuthorizationTrace(
                    item_id=item.item_id,
                    decision=decision,
                    reason_code=self._reason_code(decision, item),
                )
            )
            if decision is AccessDecision.ALLOW:
                authorized.append(item)
        return authorized, traces

    @staticmethod
    def _reason_code(decision: AccessDecision, item: SearchCandidate) -> str:
        if decision is AccessDecision.UNKNOWN:
            return "unknown_acl_or_principal"
        if item.lifecycle_state is LifecycleState.DELETED:
            return "deleted_tombstone"
        if item.lifecycle_state is LifecycleState.PENDING_RECHECK:
            return "permission_recheck_pending"
        if decision is AccessDecision.DENY:
            return "acl_denied_or_tenant_mismatch"
        return "acl_allowed"
