"""Common connector adapter boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from apps.api.domain.contracts import (
    ConnectorStatus,
    NormalizedSourceItem,
    PermissionSubjectType,
    SourceChangeEvent,
    SourcePermission,
    SourceType,
)


@dataclass(frozen=True)
class AdapterConfiguration:
    valid: bool
    capability_label: str
    error_code: str | None = None


class ConnectorAdapter:
    def __init__(
        self,
        *,
        connector_id: str,
        source_type: SourceType,
        capability_label: str,
        status: ConnectorStatus,
        capability_gaps: list[str],
    ) -> None:
        self.connector_id = connector_id
        self.source_type = source_type
        self.capability_label = capability_label
        self.status = status
        self.capability_gaps = capability_gaps

    def validate_configuration(self) -> AdapterConfiguration:
        return AdapterConfiguration(
            valid=True,
            capability_label=self.capability_label,
            error_code="LIVE_CONFIGURATION_NOT_PROVISIONED" if self.capability_label != "live" else None,
        )

    def start_initial_sync(self, sync_run_id: str, checkpoint: str | None = None) -> list[SourceChangeEvent]:
        return [
            SourceChangeEvent(
                event_id=f"event-{uuid4()}",
                sync_run_id=sync_run_id,
                operation="upsert",
                source_type=self.source_type,
                external_id="item-travel-policy",
                content_hash=f"hash-{self.source_type.value}-travel",
                acl_version="v1",
                observed_at=datetime.now(timezone.utc),
            )
        ]

    def start_incremental_sync(self, sync_run_id: str, checkpoint: str) -> list[SourceChangeEvent]:
        if self.capability_label == "blocked":
            raise RuntimeError("CONNECTOR_LIVE_ACCESS_BLOCKED")
        return self.start_initial_sync(sync_run_id, checkpoint)

    def fetch_item(self, external_id: str) -> NormalizedSourceItem:
        return NormalizedSourceItem(
            tenant_id="tenant-demo",
            connector_id=self.connector_id,
            source_type=self.source_type,
            external_id=external_id,
            title=f"{self.source_type.value.replace('_', ' ').title()} travel policy fixture",
            body=(
                f"Fixture content from {self.source_type.value}; authorized travel employees "
                "must use the approval form before booking."
            ),
            locator=f"{self.source_type.value}://fixture/{external_id}",
            content_type="text/markdown",
            content_hash=f"hash-{self.source_type.value}-{external_id}",
            lifecycle_state="active",
            acl_version="v1",
            permissions=[
                SourcePermission(
                    subject_type=PermissionSubjectType.GROUP,
                    subject_key="group-travel",
                )
            ],
            metadata={"capability_label": self.capability_label},
        )

    def fetch_permissions(self, external_id: str) -> list[SourcePermission]:
        return self.fetch_item(external_id).permissions

    def resolve_preview(self, external_id: str, locator: str) -> dict[str, str]:
        item = self.fetch_item(external_id)
        return {"title": item.title, "body": item.body, "locator": locator}

    def serialize_checkpoint(self) -> str:
        return f"checkpoint-{self.source_type.value}"
