from apps.api.data.fixture_store import FixtureStore
from apps.api.domain.contracts import SearchRequest
from apps.api.security.authorization import AuthorizationPolicy
from apps.api.services.audit import AuditService
from apps.api.services.retrieval import RetrievalService


def test_search_records_query_and_denied_candidate_audit_without_content() -> None:
    store = FixtureStore()
    audit = AuditService()
    service = RetrievalService(store, AuthorizationPolicy(), audit)

    service.search(
        store.get_principal("denied-user"),
        SearchRequest(query="restricted project launch notes"),
    )

    assert {event.event_type for event in audit.events} >= {"query_created", "candidate_denied"}
    assert all("restricted project" not in repr(event).lower() for event in audit.events)
