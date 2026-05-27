from __future__ import annotations

from typing import Protocol

from return_play.auth import RequestContext
from return_play.models import (
    FunctionalTestCreate,
    SymptomLogCreate,
    WorkloadSessionCreate,
)


class EvidenceRepositoryBoundary(Protocol):
    def create_symptom_log(
        self,
        case_id: str,
        payload: SymptomLogCreate,
        context: RequestContext,
    ) -> dict:
        ...

    def list_symptom_logs(
        self,
        case_id: str,
        context: RequestContext,
    ) -> dict[str, list[dict]]:
        ...

    def create_functional_test(
        self,
        case_id: str,
        payload: FunctionalTestCreate,
        context: RequestContext,
    ) -> dict:
        ...

    def list_functional_tests(
        self,
        case_id: str,
        context: RequestContext,
    ) -> dict[str, list[dict]]:
        ...

    def create_workload_session(
        self,
        case_id: str,
        payload: WorkloadSessionCreate,
        context: RequestContext,
    ) -> dict:
        ...

    def list_workload_sessions(
        self,
        case_id: str,
        context: RequestContext,
    ) -> dict[str, list[dict]]:
        ...
