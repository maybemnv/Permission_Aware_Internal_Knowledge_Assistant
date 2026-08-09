from datetime import datetime, timezone

from apps.api.data.fixture_store import FixtureStore
from apps.api.domain.contracts import AccessDecision, SourceChangeEvent
from apps.api.security.authorization import AuthorizationPolicy
from apps.api.services.lifecycle import LifecycleService


def test_content_update_and_acl_version_are_stored_independently() -> None:
    store = FixtureStore()
    service = LifecycleService(store, AuthorizationPolicy())

    result = service.apply_change(
        SourceChangeEvent(
            event_id="event-content-update",
            sync_run_id="sync-1",
            operation="upsert",
            source_type="notion",
            external_id="item-travel-policy",
            content_hash="hash-content-v2",
            acl_version="acl-v2",
            observed_at=datetime.now(timezone.utc),
        )
    )
    item = store.get_item("item-travel-policy")

    assert result.lifecycle_state == "active"
    assert item is not None
    assert item.content_version == "hash-content-v2"
    assert item.acl_version == "acl-v2"


def test_permission_change_stays_pending_until_query_time_recheck() -> None:
    store = FixtureStore()
    service = LifecycleService(store, AuthorizationPolicy())
    item = store.get_item("item-travel-policy")
    assert item is not None
    store.save_item(item.model_copy(update={"acl_subjects": [], "acl_version": "acl-v3"}))

    result = service.apply_change(
        SourceChangeEvent(
            event_id="event-permission-change",
            sync_run_id="sync-2",
            operation="permission_change",
            source_type="notion",
            external_id="item-travel-policy",
            acl_version="acl-v3",
            observed_at=datetime.now(timezone.utc),
        )
    )

    assert result.lifecycle_state == "pending_recheck"
    assert service.recheck("item-travel-policy", store.get_principal("allowed-user")) is AccessDecision.DENY


def test_deletion_creates_tombstone_and_denies_future_access() -> None:
    store = FixtureStore()
    service = LifecycleService(store, AuthorizationPolicy())

    result = service.apply_change(
        SourceChangeEvent(
            event_id="event-delete",
            sync_run_id="sync-3",
            operation="delete",
            source_type="notion",
            external_id="item-travel-policy",
            observed_at=datetime.now(timezone.utc),
        )
    )

    assert result.lifecycle_state == "deleted"
    assert store.get_item("item-travel-policy").lifecycle_state.value == "deleted"
