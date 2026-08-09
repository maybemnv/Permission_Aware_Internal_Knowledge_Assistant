"""Permission-filtered deterministic retrieval for fixture mode."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from uuid import uuid4

from apps.api.data.fixture_store import FixtureStore
from apps.api.domain.contracts import (
    AccessDecision,
    AuditEvent,
    FreshnessSummary,
    PrincipalContext,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from apps.api.security.authorization import AuthorizationPolicy
from apps.api.services.audit import AuditService


class RetrievalService:
    def __init__(
        self,
        store: FixtureStore,
        policy: AuthorizationPolicy,
        audit: AuditService | None = None,
    ) -> None:
        self.store = store
        self.policy = policy
        self.audit = audit or AuditService()

    def search(
        self,
        principal: PrincipalContext | None,
        request: SearchRequest,
    ) -> SearchResponse:
        query_id = f"query-{uuid4()}"
        if principal is None:
            return SearchResponse(
                query_id=query_id,
                results=[],
                answer_available=False,
                no_accessible_context=True,
                freshness_summary=FreshnessSummary(),
            )

        candidates = self.store.list_candidates(
            principal.tenant_id,
            request.query,
            request.filters,
        )
        self.audit.append(
            AuditEvent(
                event_id=f"event-{uuid4()}",
                tenant_id=principal.tenant_id,
                actor_principal_id=principal.principal_id,
                event_type="query_created",
                query_id=query_id,
                created_at=datetime.now(timezone.utc),
                metadata={
                    "query_hash": sha256(request.query.encode("utf-8")).hexdigest(),
                    "candidate_count": len(candidates),
                },
            )
        )
        authorized, traces = self.policy.filter_authorized(principal, candidates)
        for candidate, trace in zip(candidates, traces, strict=True):
            self.audit.record_decision(principal, candidate, trace)
        results = [self._to_result(item) for item in authorized[: request.limit]]
        fresh_count = sum(result.lifecycle_state.value == "active" for result in results)
        stale_count = sum(result.lifecycle_state.value == "stale" for result in results)
        return SearchResponse(
            query_id=query_id,
            results=results,
            answer_available=bool(results),
            no_accessible_context=not results,
            freshness_summary=FreshnessSummary(
                fresh_count=fresh_count,
                stale_count=stale_count,
                unknown_count=0,
            ),
        )

    @staticmethod
    def _to_result(item) -> SearchResult:
        return SearchResult(
            result_id=f"result-{item.item_id}",
            item_id=item.item_id,
            source_type=item.source_type,
            title=item.title,
            locator=item.locator,
            safe_snippet=item.body[:180],
            source_updated_at=item.source_updated_at,
            indexed_at=item.indexed_at,
            lifecycle_state=item.lifecycle_state,
            score=item.score,
        )
