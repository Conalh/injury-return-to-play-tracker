from __future__ import annotations

from typing import Protocol

from return_play.auth import RequestContext
from return_play.models import (
    AthleteSymptomCheckIn,
    GuardianAcknowledgmentCreate,
    ShareTokenCreate,
    ShareTokenRevoke,
)


class SharingReportingAuditRepositoryBoundary(Protocol):
    def create_share(
        self,
        case_id: str,
        payload: ShareTokenCreate,
        context: RequestContext,
    ) -> dict:
        ...

    def get_share(self, token: str) -> dict:
        ...

    def create_athlete_symptom_check_in(
        self,
        token: str,
        payload: AthleteSymptomCheckIn,
    ) -> dict:
        ...

    def create_guardian_acknowledgment(
        self,
        token: str,
        payload: GuardianAcknowledgmentCreate,
    ) -> dict:
        ...

    def revoke_share(
        self,
        share_id: str,
        payload: ShareTokenRevoke,
        context: RequestContext,
    ) -> dict:
        ...

    def build_report(self, case_id: str, context: RequestContext) -> bytes:
        ...

    def get_audit_log(
        self,
        case_id: str,
        context: RequestContext,
        event_type: str | None = None,
        actor_id: str | None = None,
        limit: int | None = None,
    ) -> dict[str, list[dict]]:
        ...
