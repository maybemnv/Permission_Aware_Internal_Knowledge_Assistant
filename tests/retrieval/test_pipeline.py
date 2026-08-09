from apps.api.data.fixture_store import FixtureStore
from apps.api.domain.contracts import (
    AnswerRequest,
    AnswerStatus,
    ApiError,
    ApiErrorCode,
    SearchFilters,
    SearchRequest,
    SourceType,
)
from apps.api.security.authorization import AuthorizationPolicy
from apps.api.services.answers import AnswerService, RecordingModelAdapter
from apps.api.services.preview import PreviewService
from apps.api.services.retrieval import RetrievalService


def test_search_filters_permissions_before_results_are_ranked() -> None:
    store = FixtureStore()
    service = RetrievalService(store, AuthorizationPolicy())

    response = service.search(
        store.get_principal("allowed-user"),
        SearchRequest(query="restricted project launch notes"),
    )

    assert response.results == []
    assert response.no_accessible_context is True


def test_travel_search_returns_two_authorized_sources_with_stable_result_ids() -> None:
    store = FixtureStore()
    service = RetrievalService(store, AuthorizationPolicy())

    response = service.search(
        store.get_principal("allowed-user"),
        SearchRequest(query="travel reimbursement policy approval form"),
    )

    assert {result.item_id for result in response.results} >= {
        "item-travel-policy",
        "item-approval-form",
    }
    assert all(result.result_id == f"result-{result.item_id}" for result in response.results)
    assert response.freshness_summary.fresh_count >= 2


def test_source_and_date_filters_are_applied_before_authorization_output() -> None:
    store = FixtureStore()
    service = RetrievalService(store, AuthorizationPolicy())

    response = service.search(
        store.get_principal("allowed-user"),
        SearchRequest(
            query="travel reimbursement",
            filters=SearchFilters(source_types=[SourceType.NOTION]),
        ),
    )

    assert response.results
    assert {result.source_type for result in response.results} == {SourceType.NOTION}


def test_answer_uses_only_authorized_context_and_validated_citations() -> None:
    store = FixtureStore()
    model = RecordingModelAdapter()
    service = AnswerService(
        RetrievalService(store, AuthorizationPolicy()),
        store,
        AuthorizationPolicy(),
        model,
    )

    response = service.answer(
        store.get_principal("allowed-user"),
        AnswerRequest(question="What is the travel reimbursement policy for my region and role?"),
    )

    assert response.status is AnswerStatus.ANSWERED
    assert len(response.citations) >= 2
    assert "30 days" in (response.answer_text or "")
    assert all("restricted project" not in context.lower() for context in model.contexts)


def test_denied_question_returns_safe_refusal_without_model_call() -> None:
    store = FixtureStore()
    model = RecordingModelAdapter()
    service = AnswerService(
        RetrievalService(store, AuthorizationPolicy()),
        store,
        AuthorizationPolicy(),
        model,
    )

    response = service.answer(
        store.get_principal("denied-user"),
        AnswerRequest(question="Show details of the restricted project"),
    )

    assert response.status is AnswerStatus.REFUSED
    assert response.answer_text is None
    assert response.citations == []
    assert model.contexts == []


def test_preview_rechecks_current_permission_and_returns_safe_error() -> None:
    store = FixtureStore()
    service = PreviewService(store, AuthorizationPolicy())

    allowed_preview = service.open(store.get_principal("allowed-user"), "result-item-travel-policy")
    denied_preview = service.open(store.get_principal("denied-user"), "result-item-restricted-project")

    assert allowed_preview.item_id == "item-travel-policy"
    assert isinstance(denied_preview, ApiError)
    assert denied_preview.code is ApiErrorCode.NO_ACCESSIBLE_CONTEXT
    assert "restricted" not in denied_preview.message.lower()
