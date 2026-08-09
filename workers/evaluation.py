"""Queue-facing wrapper for repeatable evaluation runs."""

from apps.api.domain.contracts import EvaluationRun
from apps.api.services.evaluation import EvaluationService


class EvaluationWorker:
    def __init__(self, service: EvaluationService) -> None:
        self.service = service

    def run(self, dataset_version: str) -> EvaluationRun:
        return self.service.run(dataset_version)
