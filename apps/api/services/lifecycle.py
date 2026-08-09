"""Content and ACL lifecycle transitions with request-time rechecks."""

from __future__ import annotations

from dataclasses import dataclass

from apps.api.data.fixture_store import FixtureStore
from apps.api.domain.contracts import (
    AccessDecision,
    LifecycleState,
    PrincipalContext,
    SourceChangeEvent,
)
from apps.api.security.authorization import AuthorizationPolicy


@dataclass(frozen=True)
class LifecycleResult:
    item_id: str
    lifecycle_state: str
    content_version: str
    acl_version: str


class LifecycleService:
    def __init__(self, store: FixtureStore, policy: AuthorizationPolicy) -> None:
        self.store = store
        self.policy = policy

    def apply_change(self, event: SourceChangeEvent) -> LifecycleResult:
        item = self.store.get_item(event.external_id)
        if item is None:
            raise KeyError(event.external_id)
        if event.operation == "delete":
            updated = item.model_copy(update={"lifecycle_state": LifecycleState.DELETED})
        elif event.operation == "permission_change":
            updated = item.model_copy(
                update={
                    "lifecycle_state": LifecycleState.PENDING_RECHECK,
                    "acl_version": event.acl_version or item.acl_version,
                }
            )
        else:
            updated = item.model_copy(
                update={
                    "lifecycle_state": LifecycleState.ACTIVE,
                    "content_version": event.content_hash or item.content_version,
                    "acl_version": event.acl_version or item.acl_version,
                }
            )
        self.store.save_item(updated)
        return LifecycleResult(
            item_id=updated.item_id,
            lifecycle_state=updated.lifecycle_state.value,
            content_version=updated.content_version,
            acl_version=updated.acl_version,
        )

    def recheck(self, item_id: str, principal: PrincipalContext | None) -> AccessDecision:
        item = self.store.get_item(item_id)
        if item is None:
            return AccessDecision.UNKNOWN
        return self.policy.evaluate(principal, item)
