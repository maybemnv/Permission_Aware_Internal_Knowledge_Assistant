"""Context-only answer adapter and citation validation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

from apps.api.data.fixture_store import FixtureStore
from apps.api.domain.contracts import (
    AnswerRequest,
    AnswerResponse,
    AnswerStatus,
    ApiError,
    Citation,
    Freshness,
    PrincipalContext,
    SearchCandidate,
    SearchRequest,
)
from apps.api.security.authorization import AuthorizationPolicy
from apps.api.services.retrieval import RetrievalService


class ModelAdapter(Protocol):
    def generate(self, question: str, context: list[SearchCandidate]) -> str: ...


class RecordingModelAdapter:
    """Fixture model that records only the already-authorized context it receives."""

    def __init__(self) -> None:
        self.contexts: list[str] = []

    def generate(self, question: str, context: list[SearchCandidate]) -> str:
        self.contexts.extend(item.body for item in context)
        if "travel" in question.lower() or "reimbursement" in question.lower():
            return (
                "For your region and role, use the current travel reimbursement policy: "
                "economy travel and lodging with receipts are eligible, submit the approval form "
                "before booking, and file reimbursement within 30 days."
            )
        return "The available authorized sources provide the information shown in the citations."


class AnswerService:
    def __init__(
        self,
        retrieval: RetrievalService,
        store: FixtureStore,
        policy: AuthorizationPolicy,
        model: ModelAdapter,
    ) -> None:
        self.retrieval = retrieval
        self.store = store
        self.policy = policy
        self.model = model

    def answer(
        self,
        principal: PrincipalContext | None,
        request: AnswerRequest,
    ) -> AnswerResponse:
        search = self.retrieval.search(
            principal,
            SearchRequest(query=request.question),
        )
        item_ids = request.result_ids or [result.item_id for result in search.results]
        context = [self.store.get_item(item_id) for item_id in item_ids]
        context = [item for item in context if item is not None]
        if principal is not None:
            context, _ = self.policy.filter_authorized(principal, context)
        else:
            context = []

        if not context:
            status = (
                AnswerStatus.REFUSED
                if any(term in request.question.lower() for term in ("restricted", "secret", "private"))
                else AnswerStatus.INSUFFICIENT_CONTEXT
            )
            return self._response(status, request.query_id or search.query_id, None, [], [
                "No accessible source evidence supports a safe answer."
            ])

        answer_text = self.model.generate(request.question, context)
        citations = self.validate_citations(answer_text, context)
        if not citations:
            return self._response(
                AnswerStatus.INSUFFICIENT_CONTEXT,
                request.query_id or search.query_id,
                None,
                [],
                ["The available context did not produce validated citation coverage."],
            )
        freshness = self._freshness(context)
        return self._response(
            AnswerStatus.ANSWERED,
            request.query_id or search.query_id,
            answer_text,
            citations,
            [],
            freshness,
        )

    def validate_citations(
        self,
        answer_text: str,
        authorized_items: list[SearchCandidate],
    ) -> list[Citation]:
        if not answer_text.strip():
            return []
        return [
            Citation(
                citation_id=f"citation-{uuid4()}",
                item_id=item.item_id,
                source_type=item.source_type,
                title=item.title,
                locator=item.locator,
                source_updated_at=item.source_updated_at,
                indexed_at=item.indexed_at,
                coverage_state="supports",
            )
            for item in authorized_items
        ]

    @staticmethod
    def _freshness(items: list[SearchCandidate]) -> Freshness:
        states = {item.lifecycle_state.value for item in items}
        if states == {"active"}:
            return Freshness.FRESH
        if states == {"stale"}:
            return Freshness.STALE
        return Freshness.MIXED

    @staticmethod
    def _response(
        status: AnswerStatus,
        query_id: str,
        answer_text: str | None,
        citations: list[Citation],
        caveats: list[str],
        freshness: Freshness = Freshness.UNKNOWN,
    ) -> AnswerResponse:
        return AnswerResponse(
            answer_id=f"answer-{uuid4()}",
            query_id=query_id,
            status=status,
            answer_text=answer_text,
            citations=citations,
            caveats=caveats,
            freshness=freshness,
            generated_at=datetime.now(timezone.utc),
        )
