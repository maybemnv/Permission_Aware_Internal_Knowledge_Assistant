from fastapi.testclient import TestClient

from apps.api.main import app


def test_admin_connector_status_covers_all_eight_sources() -> None:
    response = TestClient(app).get(
        "/v1/connectors",
        headers={"X-Demo-Principal": "admin-user"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 8
    assert {item["capabilityLabel"] for item in response.json()} <= {
        "fixture",
        "live",
        "blocked",
        "unverified",
    }


def test_non_admin_cannot_start_or_inspect_connector_sync() -> None:
    client = TestClient(app)

    status_response = client.get(
        "/v1/connectors",
        headers={"X-Demo-Principal": "allowed-user"},
    )
    sync_response = client.post(
        "/v1/connectors/connector-google_drive/sync",
        headers={"X-Demo-Principal": "allowed-user"},
        json={"mode": "initial", "idempotencyKey": "api-sync-1"},
    )

    assert status_response.status_code == 403
    assert sync_response.status_code == 403


def test_admin_can_start_sync_and_see_categorized_failure() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/connectors/connector-slack/sync",
        headers={"X-Demo-Principal": "admin-user"},
        json={"mode": "incremental", "idempotencyKey": "api-slack-1"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "failed"
    assert response.json()["errorCount"] == 1


def test_admin_evaluation_and_audit_routes_are_redacted() -> None:
    client = TestClient(app)

    evaluation = client.post(
        "/v1/admin/evaluations",
        headers={"X-Demo-Principal": "admin-user"},
        json={"datasetVersion": "demo-v1"},
    )
    audit = client.get(
        "/v1/admin/audit",
        headers={"X-Demo-Principal": "admin-user"},
    )

    assert evaluation.status_code == 200
    assert evaluation.json()["permissionLeaks"] == 0
    assert audit.status_code == 200
    assert "Secret restricted project" not in audit.text
