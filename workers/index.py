"""Lifecycle-safe indexing job boundary."""

from __future__ import annotations

from dataclasses import dataclass

from apps.api.domain.contracts import LifecycleState, SearchCandidate


@dataclass(frozen=True)
class IndexResult:
    item_id: str
    action: str
    indexed: bool
    idempotency_key: str
    duplicate: bool = False


class IndexingWorker:
    def __init__(self) -> None:
        self._completed: dict[str, IndexResult] = {}

    def process(self, item: SearchCandidate | None) -> IndexResult:
        if item is None:
            return IndexResult(
                item_id="unknown",
                action="quarantine",
                indexed=False,
                idempotency_key="unknown",
            )
        key = f"{item.item_id}:{item.content_version}:{item.acl_version}"
        if key in self._completed:
            previous = self._completed[key]
            return IndexResult(
                item_id=previous.item_id,
                action=previous.action,
                indexed=previous.indexed,
                idempotency_key=previous.idempotency_key,
                duplicate=True,
            )
        if item.lifecycle_state is LifecycleState.DELETED:
            result = IndexResult(item.item_id, "tombstone", False, key)
        elif item.lifecycle_state is LifecycleState.PENDING_RECHECK:
            result = IndexResult(item.item_id, "quarantine", False, key)
        else:
            result = IndexResult(item.item_id, "upsert", True, key)
        self._completed[key] = result
        return result
