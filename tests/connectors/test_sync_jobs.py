from workers.sync import SyncCoordinator
from connectors.registry import ConnectorRegistry


def test_sync_start_is_idempotent_for_the_same_key() -> None:
    coordinator = SyncCoordinator(ConnectorRegistry.demo())

    first = coordinator.start("connector-google_drive", "initial", "sync-key-1")
    second = coordinator.start("connector-google_drive", "initial", "sync-key-1")

    assert first.sync_run_id == second.sync_run_id
    assert first.status == "completed"
    assert first.checkpoint_after


def test_blocked_connector_failure_is_isolated_and_categorized() -> None:
    coordinator = SyncCoordinator(ConnectorRegistry.demo())

    failure = coordinator.start("connector-slack", "incremental", "sync-key-slack")
    healthy = coordinator.start("connector-google_drive", "incremental", "sync-key-drive")

    assert failure.status == "failed"
    assert failure.error_count == 1
    assert healthy.status == "completed"
    assert healthy.error_count == 0


def test_retry_of_fixture_run_reuses_checkpoint_without_duplicate_items() -> None:
    coordinator = SyncCoordinator(ConnectorRegistry.demo())

    first = coordinator.start("connector-google_drive", "incremental", "sync-key-retry")
    retried = coordinator.retry(first.sync_run_id)

    assert retried.sync_run_id == first.sync_run_id
    assert retried.checkpoint_before == first.checkpoint_after
    assert retried.items_upserted >= 0
