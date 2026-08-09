from apps.api.data.fixture_store import FixtureStore
from workers.index import IndexingWorker


def test_indexing_worker_never_indexes_deleted_or_pending_content() -> None:
    store = FixtureStore()
    worker = IndexingWorker()

    active = worker.process(store.get_item("item-travel-policy"))
    deleted = worker.process(store.get_item("item-deleted"))
    pending = worker.process(store.get_item("item-pending-recheck"))

    assert active.action == "upsert"
    assert active.indexed is True
    assert deleted.action == "tombstone"
    assert deleted.indexed is False
    assert pending.action == "quarantine"
    assert pending.indexed is False


def test_indexing_worker_is_idempotent_for_same_content_version() -> None:
    store = FixtureStore()
    worker = IndexingWorker()
    item = store.get_item("item-travel-policy")

    first = worker.process(item)
    second = worker.process(item)

    assert first.idempotency_key == second.idempotency_key
    assert second.duplicate is True
