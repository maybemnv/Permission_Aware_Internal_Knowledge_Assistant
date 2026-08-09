from fastapi.testclient import TestClient

from apps.api.main import app


def test_health_and_ready_endpoints_are_content_free() -> None:
    client = TestClient(app)

    health = client.get("/health")
    ready = client.get("/health/ready")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert ready.status_code == 200
    assert "Travel reimbursement" not in ready.text


def test_search_endpoint_uses_server_side_demo_principal() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/search",
        headers={"X-Demo-Principal": "allowed-user"},
        json={"query": "travel reimbursement policy approval form"},
    )

    assert response.status_code == 200
    assert response.json()["results"]
    assert all(item["access"] == "allowed" for item in response.json()["results"])


def test_unknown_principal_gets_safe_authentication_error() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/search",
        headers={"X-Demo-Principal": "not-a-demo-user"},
        json={"query": "travel reimbursement policy"},
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "AUTHENTICATION_REQUIRED"
