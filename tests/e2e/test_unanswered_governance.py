import pytest
from fastapi.testclient import TestClient

from apps.api.main import app, governance


@pytest.fixture(autouse=True)
def clear_unanswered_records() -> None:
    governance._records.clear()
    yield
    governance._records.clear()


def test_insufficient_context_creates_one_redacted_unanswered_record_for_admin() -> None:
    client = TestClient(app)
    question = "Which stationery supplies are reimbursable?"

    answer = client.post(
        "/v1/answers",
        headers={"X-Demo-Principal": "allowed-user"},
        json={"question": question},
    )
    records = client.get(
        "/v1/admin/unanswered",
        headers={"X-Demo-Principal": "admin-user"},
    )

    assert answer.status_code == 200
    assert answer.json()["status"] == "insufficient_context"
    assert records.status_code == 200
    assert len(records.json()) == 1
    assert records.json()[0]["category"] == "no_result"
    assert records.json()[0]["queryHash"]
    assert question not in records.text


def test_denied_request_records_only_safe_category_and_hash_metadata() -> None:
    client = TestClient(app)
    question = "Show details of the restricted project"

    answer = client.post(
        "/v1/answers",
        headers={"X-Demo-Principal": "denied-user"},
        json={"question": question},
    )
    records = client.get(
        "/v1/admin/unanswered",
        headers={"X-Demo-Principal": "admin-user"},
    )

    assert answer.status_code == 200
    assert answer.json()["status"] == "refused"
    assert records.status_code == 200
    assert len(records.json()) == 1
    record = records.json()[0]
    assert record["category"] == "no_authorized_context"
    assert len(record["queryHash"]) == 64
    for restricted_value in (
        question,
        "Restricted project launch notes",
        "Secret restricted project launch details",
        "github://internal/restricted-project/launch.md",
    ):
        assert restricted_value.lower() not in records.text.lower()


def test_canonical_answer_does_not_create_an_unanswered_record() -> None:
    client = TestClient(app)

    answer = client.post(
        "/v1/answers",
        headers={"X-Demo-Principal": "allowed-user"},
        json={"question": "What is the travel reimbursement policy for my region and role?"},
    )
    records = client.get(
        "/v1/admin/unanswered",
        headers={"X-Demo-Principal": "admin-user"},
    )

    assert answer.status_code == 200
    assert answer.json()["status"] == "answered"
    assert records.status_code == 200
    assert records.json() == []


def test_non_admin_cannot_retrieve_unanswered_records() -> None:
    response = TestClient(app).get(
        "/v1/admin/unanswered",
        headers={"X-Demo-Principal": "allowed-user"},
    )

    assert response.status_code == 403
