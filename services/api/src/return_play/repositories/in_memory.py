from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe
from uuid import uuid4

from fastapi import HTTPException, status

from return_play.audit import AuditEventType
from return_play.auth import RequestContext
from return_play.models import (
    AthleteSymptomCheckIn,
    ClinicianNoteCreate,
    GuardianAcknowledgmentCreate,
    InjuryCaseCreate,
    InjuryCaseStatus,
    MilestoneResultStatus,
    MilestoneResultUpdate,
    OrganizationCreate,
    PhaseStatus,
    ShareAudience,
    ShareTokenCreate,
    ShareTokenRevoke,
    UserCreate,
    UserDeactivateRequest,
    UserRoleUpdate,
)
from return_play.permissions import Permission, assert_permission
from return_play.privacy import filter_share_view
from return_play.repositories.demo import DemoSeedService
from return_play.repositories.in_memory_parts.athletes import InMemoryAthleteRepositoryMixin
from return_play.repositories.in_memory_parts.evidence import InMemoryEvidenceRepositoryMixin
from return_play.repositories.in_memory_parts.readiness import (
    InMemoryReadinessRepositoryMixin,
)
from return_play.repositories.in_memory_parts.templates import (
    InMemoryTemplatePlanRepositoryMixin,
)
from return_play.reports import build_case_report_pdf


class InMemoryWorkflowRepository(
    InMemoryAthleteRepositoryMixin,
    InMemoryTemplatePlanRepositoryMixin,
    InMemoryEvidenceRepositoryMixin,
    InMemoryReadinessRepositoryMixin,
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

    def create_injury_case(self, payload: InjuryCaseCreate, context: RequestContext) -> dict:
        assert_permission(context, Permission.MANAGE_CLINICAL_CASES)
        self._ensure_active_user(context)
        self._ensure_payload_organization(payload.organization_id, context)
        athlete = self.athletes.get(payload.athlete_id)
        if athlete is None or athlete["organization_id"] != context.organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Athlete not found.",
            )

        injury_case = payload.model_dump(mode="json")
        injury_case["id"] = self._new_id("case")
        now = self._now()
        injury_case["created_at"] = now
        injury_case["updated_at"] = now
        self.injury_cases[injury_case["id"]] = injury_case
        return injury_case

    def list_injury_cases(
        self,
        context: RequestContext,
        organization_id: str | None = None,
    ) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_CLINICAL_CASES)
        self._ensure_active_user(context)
        self._ensure_requested_organization(organization_id, context)
        injury_cases = [
            injury_case
            for injury_case in self.injury_cases.values()
            if injury_case["organization_id"] == context.organization_id
        ]
        return {"items": injury_cases}

    def get_injury_case_detail(self, case_id: str, context: RequestContext) -> dict:
        assert_permission(context, Permission.READ_CLINICAL_CASES)
        self._ensure_active_user(context)
        injury_case = self._get_case(case_id, context.organization_id)
        phases = self.case_plans.get(case_id, [])
        current_phase = next(
            (phase for phase in phases if self._is_active_phase(phase)),
            None,
        )
        return {
            **injury_case,
            "phases": phases,
            "current_phase": current_phase,
            "notes": self.notes.get(case_id, []),
            "symptom_logs": self.symptom_logs.get(case_id, []),
            "functional_tests": self.functional_tests.get(case_id, []),
            "workload_sessions": self.workload_sessions.get(case_id, []),
            "clearance_decisions": self.clearance_decisions.get(case_id, []),
        }

    def list_case_phases(self, case_id: str, context: RequestContext) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_CLINICAL_CASES)
        self._ensure_active_user(context)
        self._get_case(case_id, context.organization_id)
        return {"items": self.case_plans.get(case_id, [])}

    def update_milestone(
        self,
        case_id: str,
        milestone_id: str,
        payload: MilestoneResultUpdate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_CLINICAL_CASES)
        self._ensure_active_user(context)
        self._get_case(case_id, context.organization_id)
        phases = self.case_plans.get(case_id)
        if phases is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Applied case plan not found.",
            )

        for phase in phases:
            for milestone in phase["milestones"]:
                if milestone["id"] == milestone_id:
                    milestone["status"] = payload.status.value
                    milestone["recorded_by"] = payload.recorded_by
                    milestone["recorded_at"] = self._now()
                    milestone["notes"] = payload.notes
                    milestone["evidence_json"] = payload.evidence_json
                    self._record_audit_event(
                        case_id,
                        "milestone_evidence_recorded",
                        payload.recorded_by,
                        {
                            "milestone_id": milestone_id,
                            "status": payload.status.value,
                        },
                    )
                    return milestone

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found for injury case.",
        )

    def create_note(
        self,
        case_id: str,
        payload: ClinicianNoteCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_CLINICAL_CASES)
        self._ensure_active_user(context)
        self._get_case(case_id, context.organization_id)
        note = payload.model_dump(mode="json")
        note["id"] = self._new_id("note")
        note["injury_case_id"] = case_id
        note["created_at"] = self._now()
        self.notes.setdefault(case_id, []).append(note)
        return note

    def create_share(
        self,
        case_id: str,
        payload: ShareTokenCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_SHARES)
        self._ensure_active_user(context)
        self._validate_evidence_case(case_id, payload.injury_case_id, context)
        raw_token = token_urlsafe(24)
        token_hash = self._hash_token(raw_token)
        now = datetime.now(UTC)
        share = {
            **payload.model_dump(mode="json"),
            "id": self._new_id("share"),
            "token": raw_token,
            "token_hash": token_hash,
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(days=payload.expires_in_days)).isoformat(),
            "revoked_at": None,
        }
        self.share_tokens[token_hash] = share
        self._record_audit_event(
            case_id,
            "share_created",
            context.actor_id,
            {"audience": payload.audience.value, "share_id": share["id"]},
        )
        return share

    def get_share(self, token: str) -> dict:
        share = self._get_active_share_by_token(token)

        injury_case = self._get_case(share["injury_case_id"])
        athlete = self.athletes[injury_case["athlete_id"]]
        phases = self.case_plans.get(injury_case["id"], [])
        current_phase = next(
            (phase for phase in phases if self._is_active_phase(phase)),
            None,
        )
        self._record_audit_event(
            injury_case["id"],
            AuditEventType.SHARE_VIEW_READ.value,
            None,
            {"audience": share["audience"], "share_id": share["id"]},
        )
        return filter_share_view(
            {
                "audience": share["audience"],
                "athlete_name": athlete["name"],
                "sport": athlete["sport"],
                "injury_title": injury_case["title"],
                "current_phase": current_phase["name"] if current_phase else None,
                "participation_status": "Modified participation",
                "allowed_activities": share["allowed_activities"],
                "restricted_activities": share["restricted_activities"],
                "next_review_date": share["next_review_date"],
                "clearance_status": (
                    "Awaiting named clinician decision. "
                    "This shared view is not medical clearance."
                ),
                "clinician_note": share["clinician_note"],
            },
            audience=share["audience"],
        )

    def create_athlete_symptom_check_in(
        self,
        token: str,
        payload: AthleteSymptomCheckIn,
    ) -> dict:
        share = self._get_active_share_by_token(token)
        if share["audience"] != ShareAudience.ATHLETE.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Symptom check-ins require an athlete share.",
            )
        injury_case = self._get_case(share["injury_case_id"])
        symptom_log = {
            **payload.model_dump(mode="json"),
            "id": self._new_id("symptom"),
            "injury_case_id": injury_case["id"],
            "athlete_id": injury_case["athlete_id"],
            "recorded_at": self._now(),
        }
        self.symptom_logs.setdefault(injury_case["id"], []).append(symptom_log)
        self._record_audit_event(
            injury_case["id"],
            "athlete_symptom_check_in",
            injury_case["athlete_id"],
            {"symptom_log_id": symptom_log["id"], "share_id": share["id"]},
        )
        return symptom_log

    def create_guardian_acknowledgment(
        self,
        token: str,
        payload: GuardianAcknowledgmentCreate,
    ) -> dict:
        share = self._get_active_share_by_token(token)
        if share["audience"] != ShareAudience.GUARDIAN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acknowledgments require a guardian share.",
            )
        acknowledgment = {
            **payload.model_dump(mode="json"),
            "id": self._new_id("guardian_ack"),
            "share_id": share["id"],
            "injury_case_id": share["injury_case_id"],
            "created_at": self._now(),
        }
        self._record_audit_event(
            share["injury_case_id"],
            "guardian_acknowledgment_recorded",
            None,
            {
                "share_id": share["id"],
                "acknowledged_by": acknowledgment["acknowledged_by"],
                "relationship": acknowledgment["relationship"],
            },
        )
        return acknowledgment

    def revoke_share(
        self,
        token: str,
        payload: ShareTokenRevoke,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_SHARES)
        self._ensure_active_user(context)
        share = self._get_share_by_token(token)
        self._get_case(share["injury_case_id"], context.organization_id)
        if payload.revoked_by != context.actor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Revocation actor must match request context.",
            )
        if share["revoked_at"] is None:
            share["revoked_at"] = self._now()
            self._record_audit_event(
                share["injury_case_id"],
                "share_revoked",
                context.actor_id,
                {"audience": share["audience"], "share_id": share["id"]},
            )
        return share

    def build_report(self, case_id: str, context: RequestContext) -> bytes:
        assert_permission(context, Permission.GENERATE_REPORTS)
        self._ensure_active_user(context)
        injury_case = self._get_case(case_id, context.organization_id)
        athlete = self.athletes[injury_case["athlete_id"]]
        readiness = self.get_readiness(case_id, context)
        self._record_audit_event(
            case_id,
            AuditEventType.REPORT_GENERATED.value,
            context.actor_id,
            {"format": "pdf"},
        )
        self._record_audit_event(
            case_id,
            AuditEventType.SENSITIVE_EXPORT_READ.value,
            context.actor_id,
            {"export_type": "case_report", "format": "pdf"},
        )
        return build_case_report_pdf(
            {
                **self.get_injury_case_detail(case_id, context),
                "athlete_name": athlete["name"],
            },
            readiness,
            self._audit_log_copies(self.audit_log_entries.get(case_id, [])),
        )

    def get_audit_log(
        self,
        case_id: str,
        context: RequestContext,
        event_type: str | None = None,
        actor_id: str | None = None,
        limit: int | None = None,
    ) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_AUDIT_LOG)
        self._ensure_active_user(context)
        self._get_case(case_id, context.organization_id)
        events = self.audit_log_entries.get(case_id, [])
        if event_type is not None:
            events = [event for event in events if event["event_type"] == event_type]
        if actor_id is not None:
            events = [event for event in events if event["actor_id"] == actor_id]
        if limit is not None:
            events = events[:limit]
        return {"items": self._audit_log_copies(events)}

    def seed_demo(self, context: RequestContext) -> dict:
        assert_permission(context, Permission.SEED_DEMO)
        self._ensure_active_user(context)
        return DemoSeedService(self).seed_demo(context)

    def setup_organization(self, payload: OrganizationCreate, context: RequestContext) -> dict:
        assert_permission(context, Permission.MANAGE_ORGANIZATION)
        self._ensure_active_user(context)
        organization = {
            "id": context.organization_id,
            **payload.model_dump(mode="json"),
        }
        self.organizations[organization["id"]] = organization
        self._record_organization_audit_event(
            organization["id"],
            "organization_configured",
            context.actor_id,
            None,
            {"name": organization["name"], "timezone": organization["timezone"]},
        )
        return organization

    def invite_user(self, payload: UserCreate, context: RequestContext) -> dict:
        assert_permission(context, Permission.MANAGE_USERS)
        self._ensure_active_user(context)
        self._ensure_payload_organization(payload.organization_id, context)
        self.organizations.setdefault(
            payload.organization_id,
            {"id": payload.organization_id, "name": payload.organization_id, "timezone": "UTC"},
        )
        user = {
            "id": self._new_id("user"),
            **payload.model_dump(mode="json"),
            "active": True,
        }
        self.users[user["id"]] = user
        self._record_organization_audit_event(
            payload.organization_id,
            "user_invited",
            context.actor_id,
            user["id"],
            {"email": user["email"], "role": user["role"]},
        )
        return user

    def update_user_role(
        self,
        user_id: str,
        payload: UserRoleUpdate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_USERS)
        self._ensure_active_user(context)
        user = self._get_user(user_id, context.organization_id)
        previous_role = user["role"]
        user["role"] = payload.role.value
        self._record_organization_audit_event(
            context.organization_id,
            "user_role_updated",
            context.actor_id,
            user_id,
            {"previous_role": previous_role, "new_role": user["role"]},
        )
        return user

    def deactivate_user(
        self,
        user_id: str,
        payload: UserDeactivateRequest,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_USERS)
        self._ensure_active_user(context)
        if payload.deactivated_by != context.actor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Deactivation actor must match request context.",
            )
        user = self._get_user(user_id, context.organization_id)
        user["active"] = False
        self._record_organization_audit_event(
            context.organization_id,
            "user_deactivated",
            context.actor_id,
            user_id,
            {"email": user["email"], "role": user["role"]},
        )
        return user

    def get_organization_audit_log(
        self,
        organization_id: str | None,
        context: RequestContext,
    ) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_ORGANIZATION_AUDIT_LOG)
        self._ensure_active_user(context)
        self._ensure_requested_organization(organization_id, context)
        return {"items": self.organization_audit_log_entries.get(context.organization_id, [])}

    def find_demo_case(self, context: RequestContext) -> dict | None:
        for injury_case in self.injury_cases.values():
            if (
                injury_case["organization_id"] == context.organization_id
                and injury_case["title"] == "Left ankle sprain"
                and self.athletes[injury_case["athlete_id"]]["name"] == "Riley Chen"
            ):
                return injury_case
        return None

    def demo_seed_response(
        self,
        injury_case: dict,
        context: RequestContext,
        *,
        already_seeded: bool,
    ) -> dict:
        athlete = self.athletes[injury_case["athlete_id"]]
        phases = self.case_plans.get(injury_case["id"], [])
        current_phase = next(
            (phase for phase in phases if self._is_active_phase(phase)),
            None,
        )
        share = next(
            (
                share_token
                for share_token in self.share_tokens.values()
                if share_token["injury_case_id"] == injury_case["id"]
                and share_token["audience"] == "coach"
                and share_token["revoked_at"] is None
            ),
            None,
        )
        readiness = self.get_readiness(injury_case["id"], context)

        return {
            "athlete_id": athlete["id"],
            "athlete_name": athlete["name"],
            "injury_case_id": injury_case["id"],
            "current_phase": current_phase["name"] if current_phase else None,
            "share_token": share["token"] if share else None,
            "can_auto_clear": readiness["can_auto_clear"],
            "readiness_signal_count": len(readiness["signals"]),
            "already_seeded": already_seeded,
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

    @staticmethod
    def _audit_log_copies(events: list[dict]) -> list[dict]:
        return [deepcopy(event) for event in events]

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
