"""FastAPI application entrypoint for the permission-aware prototype."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse

from apps.api.config import Settings
from apps.api.data.fixture_store import FixtureStore
from apps.api.data.postgres_store import PostgresStore
from apps.api.domain.contracts import (
    AnswerRequest,
    AnswerResponse,
    AnswerStatus,
    AuditEvent,
    ApiError,
    ApiErrorCode,
    FeedbackRequest,
    HealthResponse,
    EvaluationStartRequest,
    PrincipalContext,
    ReadinessResponse,
    SearchRequest,
    SearchResponse,
    SourcePreview,
    SyncStartRequest,
)
from connectors.registry import ConnectorRegistry
from apps.api.security.authorization import AuthorizationPolicy
from apps.api.services.answers import AnswerService, RecordingModelAdapter
from apps.api.services.audit import AuditService
from apps.api.services.evaluation import EvaluationService
from apps.api.services.governance import GovernanceService
from apps.api.services.preview import PreviewService
from apps.api.services.retrieval import RetrievalService
from workers.sync import SyncCoordinator


settings = Settings.from_env()
store = FixtureStore() if settings.app_mode == "fixture" else PostgresStore(settings.database_url or "")
policy = AuthorizationPolicy()
audit = AuditService()
retrieval = RetrievalService(store, policy, audit)
model = RecordingModelAdapter()
answers = AnswerService(retrieval, store, policy, model)
previews = PreviewService(store, policy)
connector_registry = ConnectorRegistry.demo()
syncs = SyncCoordinator(connector_registry)
governance = GovernanceService(store)
evaluations = EvaluationService(store, retrieval, answers)

app = FastAPI(
    title="Permission-Aware Internal Knowledge Assistant",
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None,
)


def require_principal(demo_principal: str | None, authorization: str | None = None) -> PrincipalContext:
    if settings.app_mode == "fixture":
        principal_key = demo_principal or ""
    else:
        expected = f"Bearer {__import__('os').environ.get('AUTH_BEARER_TOKEN', '')}"
        if authorization != expected:
            raise HTTPException(status_code=401, detail="authenticated principal required")
        principal_key = __import__('os').environ["AUTH_PRINCIPAL_KEY"]
    principal = store.get_principal(principal_key)
    if principal is None:
        error = ApiError(
            code=ApiErrorCode.AUTHENTICATION_REQUIRED,
            message="A recognized demo principal is required.",
            request_id="request-authentication-required",
            retryable=False,
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error.model_dump(mode="json", by_alias=True))
    return principal


def require_admin(demo_principal: str | None, authorization: str | None = None) -> PrincipalContext:
    principal = require_principal(demo_principal, authorization)
    if not principal.is_administrator:
        error = ApiError(
            code=ApiErrorCode.AUTHORIZATION_DENIED,
            message="This administrative action is not available to the current principal.",
            request_id="request-authorization-denied",
            retryable=False,
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error.model_dump(mode="json", by_alias=True))
    return principal


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    mode = "postgres" if settings.app_mode == "postgres" else "fixture"
    return HealthResponse(status="ok", service="fixture-api" if mode == "fixture" else "api", mode=mode)


@app.get("/health/ready", response_model=ReadinessResponse)
def readiness() -> ReadinessResponse:
    fixture_mode = settings.app_mode == "fixture"
    database_state = "unavailable" if fixture_mode else ("ok" if settings.database_url else "degraded")
    status_value = "ready" if fixture_mode or database_state == "ok" else "degraded"
    return ReadinessResponse(
        status=status_value,
        checks={
            "api": "ok",
            "fixture_store": "ok" if fixture_mode else "unavailable",
            "database": database_state,
            "worker": "ok" if settings.queue_provider == "inline" else "degraded",
            "connectors": "ok",
            "index": "ok" if settings.search_provider == "fixture" else "degraded",
        },
    )


@app.post("/v1/search", response_model=SearchResponse)
def search(request: SearchRequest, x_demo_principal: str | None = Header(default=None, alias="X-Demo-Principal"), authorization: str | None = Header(default=None)) -> SearchResponse:
    return retrieval.search(require_principal(x_demo_principal, authorization), request)


@app.post("/v1/answers", response_model=AnswerResponse)
def answer(request: AnswerRequest, x_demo_principal: str | None = Header(default=None, alias="X-Demo-Principal"), authorization: str | None = Header(default=None)) -> AnswerResponse:
    principal = require_principal(x_demo_principal, authorization)
    response = answers.answer(principal, request)
    if response.status is not AnswerStatus.ANSWERED:
        governance.record_unanswered(
            query_id=str(response.query_id),
            category=(
                "no_authorized_context"
                if response.status is AnswerStatus.REFUSED
                else "no_result"
            ),
            safe_summary="No safe cited answer was available for this request.",
            tenant_id=str(principal.tenant_id),
            query_fingerprint=" ".join(request.question.casefold().split()),
        )
    return response


@app.get("/v1/results/{result_id}/preview", response_model=SourcePreview)
def preview(result_id: str, x_demo_principal: str | None = Header(default=None, alias="X-Demo-Principal"), authorization: str | None = Header(default=None)) -> SourcePreview:
    result = previews.open(require_principal(x_demo_principal, authorization), result_id)
    if isinstance(result, ApiError):
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content=result.model_dump(mode="json", by_alias=True))
    return result


@app.post("/v1/feedback")
def feedback(request: FeedbackRequest, x_demo_principal: str | None = Header(default=None, alias="X-Demo-Principal"), authorization: str | None = Header(default=None)) -> dict[str, str]:
    principal = require_principal(x_demo_principal, authorization)
    audit.append(
        AuditEvent(
            event_id=f"event-feedback-{request.query_id}",
            tenant_id=principal.tenant_id,
            actor_principal_id=principal.principal_id,
            event_type="feedback_submitted",
            query_id=request.query_id,
            created_at=datetime.now(timezone.utc),
            metadata={"rating": request.rating},
        )
    )
    return {"status": "recorded"}


@app.get("/v1/connectors")
def connector_status(x_demo_principal: str | None = Header(default=None, alias="X-Demo-Principal"), authorization: str | None = Header(default=None)):
    require_admin(x_demo_principal, authorization)
    return connector_registry.statuses()


@app.post("/v1/connectors/{connector_id}/sync")
def start_sync(
    connector_id: str,
    request: SyncStartRequest,
    x_demo_principal: str | None = Header(default=None, alias="X-Demo-Principal"),
    authorization: str | None = Header(default=None),
):
    require_admin(x_demo_principal, authorization)
    return syncs.start(connector_id, request.mode, request.idempotency_key)


@app.get("/v1/connectors/{connector_id}/sync-runs")
def sync_history(
    connector_id: str,
    x_demo_principal: str | None = Header(default=None, alias="X-Demo-Principal"),
    authorization: str | None = Header(default=None),
):
    require_admin(x_demo_principal, authorization)
    return [run for run in syncs.runs.values() if run.connector_id == connector_id]


@app.get("/v1/admin/unanswered")
def unanswered(x_demo_principal: str | None = Header(default=None, alias="X-Demo-Principal"), authorization: str | None = Header(default=None)):
    principal = require_admin(x_demo_principal, authorization)
    return governance.unanswered(principal)


@app.get("/v1/admin/evaluations")
def evaluation_history(x_demo_principal: str | None = Header(default=None, alias="X-Demo-Principal"), authorization: str | None = Header(default=None)):
    require_admin(x_demo_principal, authorization)
    return evaluations.runs


@app.post("/v1/admin/evaluations")
def start_evaluation(
    request: EvaluationStartRequest,
    x_demo_principal: str | None = Header(default=None, alias="X-Demo-Principal"),
    authorization: str | None = Header(default=None),
):
    require_admin(x_demo_principal, authorization)
    return evaluations.run(request.dataset_version)


@app.get("/v1/admin/audit")
def audit_history(x_demo_principal: str | None = Header(default=None, alias="X-Demo-Principal"), authorization: str | None = Header(default=None)):
    principal = require_admin(x_demo_principal, authorization)
    return [event for event in audit.events if event.tenant_id == principal.tenant_id]
