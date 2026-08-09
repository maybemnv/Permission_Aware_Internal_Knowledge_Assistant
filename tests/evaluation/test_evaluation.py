from apps.api.data.fixture_store import FixtureStore
from apps.api.security.authorization import AuthorizationPolicy
from apps.api.services.answers import AnswerService, RecordingModelAdapter
from apps.api.services.evaluation import EvaluationService
from apps.api.services.retrieval import RetrievalService


def test_repeatable_demo_evaluation_reports_citation_and_permission_metrics() -> None:
    store = FixtureStore()
    retrieval = RetrievalService(store, AuthorizationPolicy())
    answers = AnswerService(retrieval, store, AuthorizationPolicy(), RecordingModelAdapter())
    run = EvaluationService(store, retrieval, answers).run("demo-v1")

    assert run.status == "completed"
    assert run.total_cases >= 3
    assert run.passed_cases == run.total_cases
    assert run.citation_coverage >= 0.95
    assert run.permission_leaks == 0
