"""Idempotent fixture sync coordinator."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from apps.api.domain.contracts import SyncRun
from connectors.registry import ConnectorRegistry


class SyncCoordinator:
    def __init__(self, registry: ConnectorRegistry) -> None:
        self.registry = registry
        self.runs: dict[str, SyncRun] = {}
        self.keys: dict[str, str] = {}
        self.checkpoints: dict[str, str] = {}

    def start(self, connector_id: str, mode: str, idempotency_key: str) -> SyncRun:
        existing_id = self.keys.get(idempotency_key)
        if existing_id is not None:
            return self.runs[existing_id]

        run_id = f"sync-{uuid4()}"
        adapter = self.registry.get(connector_id)
        checkpoint_before = self.checkpoints.get(connector_id)
        started = datetime.now(timezone.utc)
        if adapter is None:
            run = SyncRun(
                sync_run_id=run_id,
                connector_id=connector_id,
                mode=mode,
                status="failed",
                checkpoint_before=checkpoint_before,
                items_rejected=1,
                error_count=1,
                started_at=started,
                finished_at=datetime.now(timezone.utc),
            )
        elif adapter.capability_label == "blocked":
            run = SyncRun(
                sync_run_id=run_id,
                connector_id=connector_id,
                mode=mode,
                status="failed",
                checkpoint_before=checkpoint_before,
                items_rejected=1,
                error_count=1,
                started_at=started,
                finished_at=datetime.now(timezone.utc),
            )
        else:
            checkpoint_after = f"checkpoint-{uuid4()}"
            run = SyncRun(
                sync_run_id=run_id,
                connector_id=connector_id,
                mode=mode,
                status="completed",
                checkpoint_before=checkpoint_before,
                checkpoint_after=checkpoint_after,
                items_seen=1,
                items_upserted=1,
                started_at=started,
                finished_at=datetime.now(timezone.utc),
            )
            self.checkpoints[connector_id] = checkpoint_after

        self.keys[idempotency_key] = run_id
        self.runs[run_id] = run
        return run

    def retry(self, sync_run_id: str) -> SyncRun:
        previous = self.runs[sync_run_id]
        if previous.status != "completed":
            return previous
        checkpoint_after = f"checkpoint-{uuid4()}"
        retried = previous.model_copy(
            update={
                "checkpoint_before": previous.checkpoint_after,
                "checkpoint_after": checkpoint_after,
                "started_at": datetime.now(timezone.utc),
                "finished_at": datetime.now(timezone.utc),
            }
        )
        self.runs[sync_run_id] = retried
        self.checkpoints[previous.connector_id] = checkpoint_after
        return retried

    def get(self, sync_run_id: str) -> SyncRun | None:
        return self.runs.get(sync_run_id)
