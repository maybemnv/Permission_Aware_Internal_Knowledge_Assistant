from apps.api.data.fixture_store import FixtureStore
from apps.api.services.governance import GovernanceService


def test_unanswered_reporting_contains_safe_summary_not_source_text() -> None:
    store = FixtureStore()
    governance = GovernanceService(store)
    governance.record_unanswered("query-1", "no_authorized_context", "A safe access-limited question.", tenant_id="tenant-demo")

    records = governance.unanswered(store.get_principal("admin-user"))

    assert records
    assert all("restricted project" not in record.safe_summary.lower() for record in records)
    assert all("secret" not in record.safe_summary.lower() for record in records)


def test_non_admin_cannot_read_unanswered_records() -> None:
    store = FixtureStore()
    governance = GovernanceService(store)
    governance.record_unanswered("query-1", "no_result", "Safe summary", tenant_id="tenant-demo")

    assert governance.unanswered(store.get_principal("allowed-user")) == []
