from __future__ import annotations

from typing import Protocol

from return_play.auth import RequestContext
from return_play.models import (
    ClearanceDecisionCreate,
    ClinicianNoteCreate,
    InjuryCaseCreate,
    MilestoneResultUpdate,
)


class CaseRepositoryBoundary(Protocol):
    def create_injury_case(
        self,
        payload: InjuryCaseCreate,
        context: RequestContext,
    ) -> dict:
        ...

    def list_injury_cases(
        self,
        context: RequestContext,
        organization_id: str | None = None,
    ) -> dict[str, list[dict]]:
        ...

    def get_injury_case_detail(self, case_id: str, context: RequestContext) -> dict:
        ...

    def list_case_phases(
        self,
        case_id: str,
        context: RequestContext,
    ) -> dict[str, list[dict]]:
        ...

    def update_milestone(
        self,
        case_id: str,
        milestone_id: str,
        payload: MilestoneResultUpdate,
        context: RequestContext,
    ) -> dict:
        ...

    def create_note(
        self,
        case_id: str,
        payload: ClinicianNoteCreate,
        context: RequestContext,
    ) -> dict:
        ...

    def create_clearance_decision(
        self,
        case_id: str,
        payload: ClearanceDecisionCreate,
        context: RequestContext,
    ) -> dict:
        ...
