"""Typed contracts shared by API routes, services, workers, and the web client."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator


UUID = Annotated[str, StringConstraints(min_length=1, max_length=128)]


def _to_camel(value: str) -> str:
    head, *tail = value.split("_")
    return head + "".join(part.capitalize() for part in tail)


class ContractModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
        extra="forbid",
        use_enum_values=False,
    )


class SourceType(StrEnum):
    GOOGLE_DRIVE = "google_drive"
    SHAREPOINT = "sharepoint"
    SLACK = "slack"
    TEAMS = "teams"
    NOTION = "notion"
    CONFLUENCE = "confluence"
    JIRA = "jira"
    GITHUB = "github"


class LifecycleState(StrEnum):
    ACTIVE = "active"
    STALE = "stale"
    DELETED = "deleted"
    PENDING_RECHECK = "pending_recheck"


class AccessDecision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    UNKNOWN = "unknown"


class PermissionSubjectType(StrEnum):
    PRINCIPAL = "principal"
    GROUP = "group"
    ROLE = "role"


class ConnectorStatus(StrEnum):
    CONFIGURED = "configured"
    RUNNING = "running"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    PAUSED = "paused"


class AnswerStatus(StrEnum):
    ANSWERED = "answered"
    INSUFFICIENT_CONTEXT = "insufficient_context"
    REFUSED = "refused"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"


class Freshness(StrEnum):
    FRESH = "fresh"
    MIXED = "mixed"
    STALE = "stale"
    UNKNOWN = "unknown"


class ApiErrorCode(StrEnum):
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    AUTHORIZATION_DENIED = "AUTHORIZATION_DENIED"
    NO_ACCESSIBLE_CONTEXT = "NO_ACCESSIBLE_CONTEXT"
    CONNECTOR_UNAVAILABLE = "CONNECTOR_UNAVAILABLE"
    SYNC_ALREADY_RUNNING = "SYNC_ALREADY_RUNNING"
    INVALID_REQUEST = "INVALID_REQUEST"
    CITATION_UNAVAILABLE = "CITATION_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class PrincipalContext(ContractModel):
    tenant_id: UUID
    principal_id: UUID
    email: str
    group_ids: list[UUID] = Field(default_factory=list)
    role_labels: list[str] = Field(default_factory=list)
    region_labels: list[str] = Field(default_factory=list)
    auth_issued_at: datetime
    is_administrator: bool = False


class SearchFilters(ContractModel):
    source_types: list[SourceType] | None = None
    updated_after: datetime | None = None
    updated_before: datetime | None = None
    role_labels: list[str] | None = None
    region_labels: list[str] | None = None


class SearchRequest(ContractModel):
    query: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    filters: SearchFilters | None = None
    limit: int = Field(default=10, ge=1, le=50)
    cursor: str | None = None


class SearchResult(ContractModel):
    result_id: UUID
    item_id: UUID
    source_type: SourceType
    title: str
    locator: str
    safe_snippet: str | None = None
    source_updated_at: datetime | None = None
    indexed_at: datetime
    lifecycle_state: LifecycleState
    score: float = Field(ge=0)
    access: Literal["allowed"] = "allowed"


class FreshnessSummary(ContractModel):
    fresh_count: int = Field(default=0, ge=0)
    stale_count: int = Field(default=0, ge=0)
    unknown_count: int = Field(default=0, ge=0)


class SearchResponse(ContractModel):
    query_id: UUID
    results: list[SearchResult]
    next_cursor: str | None = None
    answer_available: bool
    no_accessible_context: bool
    freshness_summary: FreshnessSummary


class AnswerRequest(ContractModel):
    query_id: UUID | None = None
    question: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    result_ids: list[UUID] | None = None


class Citation(ContractModel):
    citation_id: UUID
    item_id: UUID
    source_type: SourceType
    title: str
    locator: str
    source_updated_at: datetime | None = None
    indexed_at: datetime
    coverage_state: Literal["supports", "partial"]


class AnswerResponse(ContractModel):
    answer_id: UUID
    query_id: UUID
    status: AnswerStatus
    answer_text: str | None = None
    citations: list[Citation]
    caveats: list[str]
    freshness: Freshness
    generated_at: datetime


class SourcePermission(ContractModel):
    subject_type: PermissionSubjectType
    subject_key: str
    permission: Literal["read"] = "read"


class NormalizedSourceItem(ContractModel):
    tenant_id: UUID
    connector_id: UUID
    source_type: SourceType
    external_id: str
    parent_external_id: str | None = None
    title: str
    body: str
    canonical_url: str | None = None
    locator: str
    content_type: str | None = None
    source_created_at: datetime | None = None
    source_updated_at: datetime | None = None
    content_hash: str
    lifecycle_state: Literal["active", "deleted"]
    acl_version: str
    permissions: list[SourcePermission]
    metadata: dict[str, str | int | float | bool | list[str]] = Field(default_factory=dict)


class SyncRun(ContractModel):
    sync_run_id: UUID
    connector_id: UUID
    mode: Literal["initial", "incremental", "reconcile"]
    status: Literal["queued", "running", "completed", "partial", "failed"]
    checkpoint_before: str | None = None
    checkpoint_after: str | None = None
    items_seen: int = 0
    items_upserted: int = 0
    items_deleted: int = 0
    items_rejected: int = 0
    error_count: int = 0
    started_at: datetime | None = None
    finished_at: datetime | None = None


class SourceChangeEvent(ContractModel):
    event_id: UUID
    sync_run_id: UUID
    operation: Literal["upsert", "delete", "permission_change"]
    source_type: SourceType
    external_id: str
    content_hash: str | None = None
    acl_version: str | None = None
    observed_at: datetime


class AuditEvent(ContractModel):
    event_id: UUID
    tenant_id: UUID
    actor_principal_id: UUID | None = None
    event_type: Literal[
        "query_created",
        "candidate_authorized",
        "candidate_denied",
        "answer_created",
        "citation_opened",
        "feedback_submitted",
        "sync_started",
        "sync_finished",
        "item_deleted",
        "permission_recheck",
    ]
    query_id: UUID | None = None
    item_id: UUID | None = None
    connector_id: UUID | None = None
    decision: AccessDecision | None = None
    reason_code: str | None = None
    created_at: datetime
    correlation_id: UUID | None = None
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class ApiError(ContractModel):
    code: ApiErrorCode
    message: str
    request_id: UUID
    retryable: bool


class SourcePreview(ContractModel):
    result_id: UUID
    item_id: UUID
    title: str
    source_type: SourceType
    locator: str
    excerpt: str
    source_updated_at: datetime | None = None
    indexed_at: datetime
    lifecycle_state: LifecycleState
    canonical_url: str | None = None


class FeedbackRequest(ContractModel):
    query_id: UUID
    answer_id: UUID | None = None
    rating: Literal["helpful", "not_helpful", "incorrect"]
    reason: str | None = Field(default=None, max_length=500)

    @field_validator("reason")
    @classmethod
    def reject_blank_reason(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            return None
        return value


class SyncStartRequest(ContractModel):
    mode: Literal["initial", "incremental", "reconcile"] = "initial"
    idempotency_key: Annotated[str, StringConstraints(min_length=1, max_length=128)]


class EvaluationStartRequest(ContractModel):
    dataset_version: Annotated[str, StringConstraints(min_length=1, max_length=64)]


class ConnectorStatusSummary(ContractModel):
    connector_id: UUID
    source_type: SourceType
    status: ConnectorStatus
    capability_label: Literal["fixture", "live", "blocked", "unverified"]
    last_successful_sync: datetime | None = None
    current_run_id: UUID | None = None
    item_count: int = Field(default=0, ge=0)
    error_count: int = Field(default=0, ge=0)
    freshness: Freshness
    capability_gaps: list[str] = Field(default_factory=list)


class UnansweredRecord(ContractModel):
    query_id: UUID
    category: Literal["no_result", "no_authorized_context", "low_citation", "negative_feedback"]
    query_hash: str
    created_at: datetime
    safe_summary: str


class EvaluationCase(ContractModel):
    case_id: UUID
    dataset_version: str
    question: str
    expected_item_ids: list[UUID]
    expected_permission: AccessDecision


class EvaluationRun(ContractModel):
    evaluation_id: UUID
    dataset_version: str
    status: Literal["queued", "running", "completed", "failed"]
    total_cases: int = Field(default=0, ge=0)
    passed_cases: int = Field(default=0, ge=0)
    citation_coverage: float = Field(default=0, ge=0, le=1)
    permission_leaks: int = Field(default=0, ge=0)
    started_at: datetime | None = None
    finished_at: datetime | None = None


class HealthResponse(ContractModel):
    status: Literal["ok", "degraded"]
    service: str
    mode: Literal["fixture", "postgres"]


class ReadinessResponse(ContractModel):
    status: Literal["ready", "degraded"]
    checks: dict[str, Literal["ok", "degraded", "unavailable"]]


class SearchCandidate(ContractModel):
    item_id: UUID
    tenant_id: UUID
    source_type: SourceType
    title: str
    body: str
    locator: str
    source_updated_at: datetime | None
    indexed_at: datetime
    lifecycle_state: LifecycleState
    acl_subjects: list[SourcePermission]
    role_labels: list[str] = Field(default_factory=list)
    region_labels: list[str] = Field(default_factory=list)
    score: float = 0
    result_id: UUID | None = None
    content_version: str = "v1"
    acl_version: str = "v1"
    canonical_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
