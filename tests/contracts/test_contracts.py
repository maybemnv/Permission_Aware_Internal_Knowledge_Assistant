from datetime import datetime, timezone

import pytest

from apps.api.domain.contracts import (
    AccessDecision,
    AnswerResponse,
    ApiError,
    Citation,
    LifecycleState,
    PrincipalContext,
    SearchResponse,
    SourceType,
)


def test_search_response_accepts_prd_camel_case_contract() -> None:
    response = SearchResponse.model_validate(
        {
            "queryId": "query-1",
            "results": [],
            "answerAvailable": False,
            "noAccessibleContext": True,
            "freshnessSummary": {
                "freshCount": 0,
                "staleCount": 0,
                "unknownCount": 0,
            },
        }
    )

    assert response.query_id == "query-1"
    assert response.no_accessible_context is True


def test_answer_contract_rejects_unknown_status() -> None:
    with pytest.raises(ValueError):
        AnswerResponse.model_validate(
            {
                "answerId": "answer-1",
                "queryId": "query-1",
                "status": "hallucinated",
                "citations": [],
                "caveats": [],
                "freshness": "unknown",
                "generatedAt": datetime.now(timezone.utc).isoformat(),
            }
        )


def test_shared_contracts_keep_safety_enums_explicit() -> None:
    assert AccessDecision.UNKNOWN.value == "unknown"
    assert LifecycleState.DELETED.value == "deleted"
    assert SourceType.GOOGLE_DRIVE.value == "google_drive"


def test_principal_and_citation_round_trip_with_aliases() -> None:
    principal = PrincipalContext.model_validate(
        {
            "tenantId": "tenant-1",
            "principalId": "principal-1",
            "email": "allowed@example.com",
            "groupIds": ["group-travel"],
            "roleLabels": ["employee"],
            "regionLabels": ["us-east"],
            "authIssuedAt": datetime.now(timezone.utc).isoformat(),
        }
    )
    citation = Citation.model_validate(
        {
            "citationId": "citation-1",
            "itemId": "item-1",
            "sourceType": "notion",
            "title": "Travel policy",
            "locator": "section:reimbursement",
            "indexedAt": datetime.now(timezone.utc).isoformat(),
            "coverageState": "supports",
        }
    )

    assert principal.group_ids == ["group-travel"]
    assert citation.source_type is SourceType.NOTION


def test_api_error_has_safe_retry_contract() -> None:
    error = ApiError(
        code="NO_ACCESSIBLE_CONTEXT",
        message="No accessible context is available for this request.",
        request_id="request-1",
        retryable=False,
    )

    assert error.model_dump(by_alias=True)["requestId"] == "request-1"
