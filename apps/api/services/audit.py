"""Redacted audit event storage for fixture mode."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from apps.api.domain.contracts import AuditEvent, PrincipalContext, SearchCandidate
from apps.api.security.authorization import AuthorizationTrace


class AuditService:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def append(self, event: AuditEvent) -> AuditEvent:
        self.events.append(event)
        return event

    def record_decision(
        self,
        principal: PrincipalContext,
        item: SearchCandidate,
        trace: AuthorizationTrace,
    ) -> AuditEvent:
        event_type = "candidate_authorized" if trace.decision.value == "allow" else "candidate_denied"
        return self.append(
            AuditEvent(
                event_id=str(uuid4()),
                tenant_id=principal.tenant_id,
                actor_principal_id=principal.principal_id,
                event_type=event_type,
                item_id=item.item_id,
                decision=trace.decision,
                reason_code=trace.reason_code,
                created_at=datetime.now(timezone.utc),
                metadata={"source_type": item.source_type.value},
            )
        )
