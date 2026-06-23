from __future__ import annotations

from datetime import UTC, datetime
from hashlib import sha256
from uuid import uuid4

from fastapi import HTTPException, status

from return_play.auth import RequestContext
from return_play.models import PhaseStatus
from return_play.repositories.in_memory_parts.administration import (
    InMemoryAdministrationRepositoryMixin,
)
from return_play.repositories.in_memory_parts.athletes import InMemoryAthleteRepositoryMixin
from return_play.repositories.in_memory_parts.cases import InMemoryCaseRepositoryMixin
from return_play.repositories.in_memory_parts.evidence import InMemoryEvidenceRepositoryMixin
from return_play.repositories.in_memory_parts.readiness import (
    InMemoryReadinessRepositoryMixin,
)
from return_play.repositories.in_memory_parts.reporting import (
    InMemoryReportingRepositoryMixin,
)
from return_play.repositories.in_memory_parts.shares import InMemoryShareRepositoryMixin
from return_play.repositories.in_memory_parts.templates import (
    InMemoryTemplatePlanRepositoryMixin,
)


class InMemoryWorkflowRepository(
    InMemoryAdministrationRepositoryMixin,
    InMemoryAthleteRepositoryMixin,
    InMemoryCaseRepositoryMixin,
    InMemoryTemplatePlanRepositoryMixin,
    InMemoryEvidenceRepositoryMixin,
    InMemoryReadinessRepositoryMixin,
    InMemoryReportingRepositoryMixin,
    InMemoryShareRepositoryMixin,
):
    def __init__(self) -> None:
        self.athletes: dict[str, dict] = {}
        self.injury_cases: dict[str, dict] = {}
        self.templates: dict[str, dict] = {}
        self.case_plans: dict[str, list[dict]] = {}
        self.notes: dict[str, list[dict]] = {}
        self.symptom_logs: dict[str, list[dict]] = {}
        self.functional_tests: dict[str, list[dict]] = {}
        self.workload_sessions: dict[str, list[dict]] = {}
        self.clearance_decisions: dict[str, list[dict]] = {}
        self.share_tokens: dict[str, dict] = {}
        self.audit_log_entries: dict[str, list[dict]] = {}
        self.organizations: dict[str, dict] = {}
        self.users: dict[str, dict] = {}
        self.organization_audit_log_entries: dict[str, list[dict]] = {}

    @staticmethod
    def _is_active_phase(phase: dict) -> bool:
        return phase["status"] in {
            PhaseStatus.CURRENT.value,
            PhaseStatus.HELD.value,
        }

    def _get_case(self, case_id: str, organization_id: str | None = None) -> dict:
        try:
            injury_case = self.injury_cases[case_id]
        except KeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Injury case not found.",
            ) from exc
        if organization_id is not None and injury_case["organization_id"] != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Injury case not found.",
            )
        return injury_case

    def _get_template(self, template_id: str, organization_id: str | None = None) -> dict:
        try:
            template = self.templates[template_id]
        except KeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found.",
            ) from exc
        if organization_id is not None and template["organization_id"] != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found.",
            )
        return template

    def _get_user(self, user_id: str, organization_id: str) -> dict:
        user = self.users.get(user_id)
        if user is None or user["organization_id"] != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return user

    def _ensure_active_user(self, context: RequestContext) -> None:
        user = self.users.get(context.actor_id)
        if user is not None and not user["active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is deactivated.",
            )

    def _validate_evidence_case(
        self,
        route_case_id: str,
        payload_case_id: str,
        context: RequestContext,
    ) -> None:
        self._get_case(route_case_id, context.organization_id)
        if route_case_id != payload_case_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evidence payload case does not match route.",
            )

    def _ensure_payload_organization(
        self,
        organization_id: str,
        context: RequestContext,
    ) -> None:
        if organization_id != context.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Payload organization does not match request context.",
            )

    def _ensure_requested_organization(
        self,
        organization_id: str | None,
        context: RequestContext,
    ) -> None:
        if organization_id is not None and organization_id != context.organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Requested organization does not match request context.",
            )

    def _get_share_by_token(self, token: str) -> dict:
        token_hash = self._hash_token(token)
        try:
            return self.share_tokens[token_hash]
        except KeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share token not found.",
            ) from exc

    def _get_active_share_by_token(self, token: str) -> dict:
        share = self._get_share_by_token(token)
        if share["revoked_at"] is not None:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Share token has been revoked.",
            )
        if datetime.fromisoformat(share["expires_at"]) <= datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Share token has expired.",
            )
        return share

    def _record_audit_event(
        self,
        case_id: str,
        event_type: str,
        actor_id: str | None,
        metadata: dict,
    ) -> dict:
        event = {
            "id": self._new_id("audit"),
            "injury_case_id": case_id,
            "event_type": event_type,
            "actor_id": actor_id,
            "created_at": self._now(),
            "metadata_json": metadata,
        }
        self.audit_log_entries.setdefault(case_id, []).append(event)
        return event

    def _record_organization_audit_event(
        self,
        organization_id: str,
        event_type: str,
        actor_id: str | None,
        target_user_id: str | None,
        metadata: dict,
    ) -> dict:
        event = {
            "id": self._new_id("org_audit"),
            "organization_id": organization_id,
            "event_type": event_type,
            "actor_id": actor_id,
            "target_user_id": target_user_id,
            "created_at": self._now(),
            "metadata_json": metadata,
        }
        self.organization_audit_log_entries.setdefault(organization_id, []).append(event)
        return event

    @staticmethod
    def _hash_token(token: str) -> str:
        return sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}_{uuid4().hex}"

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()
