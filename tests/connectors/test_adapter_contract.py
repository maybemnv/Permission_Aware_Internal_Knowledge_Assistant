from connectors.registry import ConnectorRegistry
from apps.api.domain.contracts import SourceType


def test_registry_exposes_all_eight_mvp_source_types() -> None:
    registry = ConnectorRegistry.demo()

    assert set(registry.source_types()) == set(SourceType)


def test_each_fixture_adapter_exposes_safe_capabilities_and_normalized_item() -> None:
    registry = ConnectorRegistry.demo()

    for adapter in registry.adapters():
        configuration = adapter.validate_configuration()
        item = adapter.fetch_item("item-travel-policy")

        assert configuration.valid is True
        assert adapter.capability_label in {"fixture", "blocked", "unverified"}
        assert item.source_type is adapter.source_type
        assert item.permissions
        assert "secret" not in repr(configuration).lower()


def test_status_summaries_never_return_connector_credentials() -> None:
    statuses = ConnectorRegistry.demo().statuses()

    assert len(statuses) == 8
    serialized = repr(statuses).lower()
    assert "password" not in serialized
    assert "token" not in serialized
    assert "api_key" not in serialized
