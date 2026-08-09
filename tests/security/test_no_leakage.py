from apps.api.data.fixture_store import FixtureStore
from apps.api.security.authorization import AuthorizationPolicy
from apps.api.services.audit import AuditService


def test_denied_items_are_absent_from_filtered_results() -> None:
    store = FixtureStore()
    principal = store.get_principal("denied-user")
    restricted = store.get_item("item-restricted-project")
    policy = AuthorizationPolicy()

    assert principal is not None
    assert restricted is not None
    allowed, traces = policy.filter_authorized(principal, [restricted])

    assert allowed == []
    assert traces[0].decision.value == "deny"
    assert "restricted" not in repr(allowed).lower()
    assert "secret" not in repr(allowed).lower()


def test_audit_trace_does_not_include_source_body() -> None:
    store = FixtureStore()
    principal = store.get_principal("denied-user")
    restricted = store.get_item("item-restricted-project")
    policy = AuthorizationPolicy()

    assert principal is not None
    assert restricted is not None
    _, traces = policy.filter_authorized(principal, [restricted])

    assert restricted.body not in repr(traces)
    assert restricted.title not in repr(traces)


def test_denied_decision_audit_contains_reason_but_not_content() -> None:
    store = FixtureStore()
    principal = store.get_principal("denied-user")
    restricted = store.get_item("item-restricted-project")
    policy = AuthorizationPolicy()
    audit = AuditService()

    assert principal is not None
    assert restricted is not None
    _, traces = policy.filter_authorized(principal, [restricted])
    event = audit.record_decision(principal, restricted, traces[0])

    assert event.event_type == "candidate_denied"
    assert event.reason_code == "acl_denied_or_tenant_mismatch"
    assert restricted.body not in repr(event)
    assert restricted.title not in repr(event)
