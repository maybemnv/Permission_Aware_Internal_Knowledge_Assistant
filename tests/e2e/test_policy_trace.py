from fastapi.testclient import TestClient

from apps.api.main import app


def test_canonical_allowed_user_trace_is_cited_and_previewable() -> None:
    client = TestClient(app)
    headers = {"X-Demo-Principal": "allowed-user"}
    question = "What is the travel reimbursement policy for my region and role?"

    search = client.post("/v1/search", headers=headers, json={"query": question})
    answer = client.post("/v1/answers", headers=headers, json={"question": question})

    assert search.status_code == 200
    assert answer.status_code == 200
    assert answer.json()["status"] == "answered"
    assert len(answer.json()["citations"]) >= 2
    assert {item["sourceType"] for item in answer.json()["citations"]} >= {"notion", "google_drive"}

    preview_id = answer.json()["citations"][0]["itemId"]
    preview = client.get(f"/v1/results/result-{preview_id}/preview", headers=headers)
    assert preview.status_code == 200
    assert preview.json()["itemId"] == preview_id


def test_denied_user_has_no_restricted_result_answer_or_preview_signal() -> None:
    client = TestClient(app)
    headers = {"X-Demo-Principal": "denied-user"}

    search = client.post(
        "/v1/search",
        headers=headers,
        json={"query": "Show details of the restricted project"},
    )
    answer = client.post(
        "/v1/answers",
        headers=headers,
        json={"question": "Show details of the restricted project"},
    )
    preview = client.get(
        "/v1/results/result-item-restricted-project/preview",
        headers=headers,
    )

    assert search.status_code == 200
    assert search.json()["results"] == []
    assert "restricted" not in search.text.lower()
    assert answer.status_code == 200
    assert answer.json()["status"] == "refused"
    assert answer.json()["citations"] == []
    assert preview.status_code == 403
    assert "restricted" not in preview.text.lower()
