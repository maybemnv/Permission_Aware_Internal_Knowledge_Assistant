"""Repeatable fixture evaluation for retrieval safety and citation coverage."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from apps.api.data.fixture_store import FixtureStore
from apps.api.domain.contracts import AnswerRequest, AnswerStatus, EvaluationRun
from apps.api.services.answers import AnswerService
from apps.api.services.retrieval import RetrievalService


class EvaluationService:
    def __init__(
        self,
        store: FixtureStore,
        retrieval: RetrievalService,
        answers: AnswerService,
    ) -> None:
        self.store = store
        self.retrieval = retrieval
        self.answers = answers
        self.runs: list[EvaluationRun] = []

    def run(self, dataset_version: str) -> EvaluationRun:
        started = datetime.now(timezone.utc)
        cases = [
            ("allowed-user", "What is the travel reimbursement policy for my region and role?", AnswerStatus.ANSWERED),
            ("denied-user", "Show details of the restricted project", AnswerStatus.REFUSED),
            ("allowed-user", "What are the quantum cloud controls?", AnswerStatus.INSUFFICIENT_CONTEXT),
        ]
        passed = 0
        answerable_cases = 0
        cited_answerable_cases = 0
        permission_leaks = 0
        for principal_key, question, expected_status in cases:
            response = self.answers.answer(
                self.store.get_principal(principal_key),
                AnswerRequest(question=question),
            )
            if response.status is expected_status:
                passed += 1
            if expected_status is AnswerStatus.ANSWERED:
                answerable_cases += 1
                if response.status is AnswerStatus.ANSWERED and response.citations:
                    cited_answerable_cases += 1
            if principal_key == "denied-user" and response.citations:
                permission_leaks += 1
        run = EvaluationRun(
            evaluation_id=f"evaluation-{uuid4()}",
            dataset_version=dataset_version,
            status="completed",
            total_cases=len(cases),
            passed_cases=passed,
            citation_coverage=cited_answerable_cases / max(1, answerable_cases),
            permission_leaks=permission_leaks,
            started_at=started,
            finished_at=datetime.now(timezone.utc),
        )
        self.runs.append(run)
        return run
