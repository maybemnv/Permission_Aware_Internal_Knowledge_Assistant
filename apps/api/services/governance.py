"""Redacted unanswered-question reporting."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from uuid import uuid4

from apps.api.data.fixture_store import FixtureStore
from apps.api.domain.contracts import PrincipalContext, UnansweredRecord


class GovernanceService:
    def __init__(self, store: FixtureStore) -> None:
        self.store = store
        self._records: list[UnansweredRecord] = []

    def record_unanswered(
        self,
        query_id: str,
        category: str,
        safe_summary: str,
        query_fingerprint: str | None = None,
    ) -> UnansweredRecord:
        record = UnansweredRecord(
            query_id=query_id,
            category=category,
            query_hash=sha256((query_fingerprint or query_id).encode("utf-8")).hexdigest(),
            created_at=datetime.now(timezone.utc),
            safe_summary=safe_summary[:240],
        )
        self._records.append(record)
        return record

    def unanswered(self, principal: PrincipalContext | None) -> list[UnansweredRecord]:
        if principal is None or not principal.is_administrator:
            return []
        return list(self._records)
