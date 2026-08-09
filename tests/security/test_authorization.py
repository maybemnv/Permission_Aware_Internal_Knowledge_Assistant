from apps.api.domain.contracts import AccessDecision, LifecycleState
from apps.api.security.authorization import AuthorizationPolicy
from apps.api.data.fixture_store import FixtureStore


def test_allowed_principal_can_read_regional_travel_policy() -> None:
    store = FixtureStore()
    principal = store.get_principal("allowed-user")
    item = store.get_item("item-travel-policy")

    assert principal is not None
    assert item is not None
    assert AuthorizationPolicy().evaluate(principal, item) is AccessDecision.ALLOW


def test_denied_principal_cannot_read_restricted_project() -> None:
    store = FixtureStore()
    principal = store.get_principal("denied-user")
    item = store.get_item("item-restricted-project")

    assert principal is not None
    assert item is not None
    assert AuthorizationPolicy().evaluate(principal, item) is AccessDecision.DENY


def test_unknown_principal_and_acl_are_not_promoted_to_allow() -> None:
    store = FixtureStore()
    item = store.get_item("item-unknown-acl")

    assert item is not None
    policy = AuthorizationPolicy()
    assert policy.evaluate(None, item) is AccessDecision.UNKNOWN
    assert policy.evaluate(store.get_principal("allowed-user"), item) is AccessDecision.UNKNOWN


def test_cross_tenant_item_is_denied_even_for_an_administrator() -> None:
    store = FixtureStore()
    principal = store.get_principal("admin-user")
    item = store.get_item("item-cross-tenant")

    assert principal is not None
    assert item is not None
    assert AuthorizationPolicy().evaluate(principal, item) is AccessDecision.DENY


def test_deleted_and_pending_items_never_enter_authorized_context() -> None:
    store = FixtureStore()
    principal = store.get_principal("allowed-user")
    policy = AuthorizationPolicy()

    assert principal is not None
    for item_key in ("item-deleted", "item-pending-recheck"):
        item = store.get_item(item_key)
        assert item is not None
        decision = policy.evaluate(principal, item)
        assert decision is AccessDecision.DENY
        assert item.lifecycle_state in {
            LifecycleState.DELETED,
            LifecycleState.PENDING_RECHECK,
        }
