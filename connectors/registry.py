"""Connector registry and status projection."""

from __future__ import annotations

from datetime import datetime, timezone

from apps.api.domain.contracts import ConnectorStatusSummary, ConnectorStatus, Freshness, SourceType
from connectors.base import ConnectorAdapter


class ConnectorRegistry:
    def __init__(self, adapters: dict[str, ConnectorAdapter]) -> None:
        self._adapters = adapters

    @classmethod
    def demo(cls) -> "ConnectorRegistry":
        definitions = {
            SourceType.GOOGLE_DRIVE: ("fixture", ConnectorStatus.HEALTHY, ["provider auth not configured"]),
            SourceType.SHAREPOINT: ("fixture", ConnectorStatus.DEGRADED, ["provider ACL fidelity unverified"]),
            SourceType.SLACK: ("blocked", ConnectorStatus.CONFIGURED, ["live connector blocked for prototype"]),
            SourceType.TEAMS: ("unverified", ConnectorStatus.CONFIGURED, ["capability test required"]),
            SourceType.NOTION: ("fixture", ConnectorStatus.HEALTHY, ["fixture adapter only"]),
            SourceType.CONFLUENCE: ("unverified", ConnectorStatus.CONFIGURED, ["capability test required"]),
            SourceType.JIRA: ("fixture", ConnectorStatus.DEGRADED, ["incremental feed is simulated"]),
            SourceType.GITHUB: ("blocked", ConnectorStatus.CONFIGURED, ["provider auth not configured"]),
        }
        adapters = {
            f"connector-{source_type.value}": ConnectorAdapter(
                connector_id=f"connector-{source_type.value}",
                source_type=source_type,
                capability_label=capability_label,
                status=status,
                capability_gaps=gaps,
            )
            for source_type, (capability_label, status, gaps) in definitions.items()
        }
        return cls(adapters)

    def get(self, connector_id: str) -> ConnectorAdapter | None:
        return self._adapters.get(connector_id)

    def adapters(self) -> list[ConnectorAdapter]:
        return list(self._adapters.values())

    def source_types(self) -> list[SourceType]:
        return [adapter.source_type for adapter in self.adapters()]

    def statuses(self) -> list[ConnectorStatusSummary]:
        now = datetime.now(timezone.utc)
        return [
            ConnectorStatusSummary(
                connector_id=adapter.connector_id,
                source_type=adapter.source_type,
                status=adapter.status,
                capability_label=adapter.capability_label,
                last_successful_sync=now if adapter.status is ConnectorStatus.HEALTHY else None,
                item_count=1 if adapter.capability_label == "fixture" else 0,
                error_count=1 if adapter.status is ConnectorStatus.DEGRADED else 0,
                freshness=Freshness.FRESH if adapter.status is ConnectorStatus.HEALTHY else Freshness.UNKNOWN,
                capability_gaps=adapter.capability_gaps,
            )
            for adapter in self.adapters()
        ]
