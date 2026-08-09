"""Fresh permission-checked source previews."""

from __future__ import annotations

from datetime import datetime, timezone

from apps.api.data.fixture_store import FixtureStore
from apps.api.domain.contracts import (
    AccessDecision,
    ApiError,
    ApiErrorCode,
    LifecycleState,
    PrincipalContext,
    SourcePreview,
)
from apps.api.security.authorization import AuthorizationPolicy


class PreviewService:
    def __init__(self, store: FixtureStore, policy: AuthorizationPolicy) -> None:
        self.store = store
        self.policy = policy

    def open(
        self,
        principal: PrincipalContext | None,
        result_id: str,
    ) -> SourcePreview | ApiError:
        item_id = result_id.removeprefix("result-")
        item = self.store.get_item(item_id)
        if principal is None or item is None:
            return self._safe_error("preview-not-available")
        decision = self.policy.evaluate(principal, item)
        if decision is not AccessDecision.ALLOW:
            return self._safe_error("preview-not-available")
        return SourcePreview(
            result_id=result_id,
            item_id=item.item_id,
            title=item.title,
            source_type=item.source_type,
            locator=item.locator,
            excerpt=item.body[:400],
            source_updated_at=item.source_updated_at,
            indexed_at=item.indexed_at,
            lifecycle_state=item.lifecycle_state,
            canonical_url=item.canonical_url,
        )

    @staticmethod
    def _safe_error(request_id: str) -> ApiError:
        return ApiError(
            code=ApiErrorCode.NO_ACCESSIBLE_CONTEXT,
            message="No accessible source preview is available for this request.",
            request_id=request_id,
            retryable=False,
        )
