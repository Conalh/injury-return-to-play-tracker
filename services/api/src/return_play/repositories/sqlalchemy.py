from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from return_play.audit import AuditEventType
from return_play.auth import RequestContext
from return_play.db import (
    Athlete,
    AuditLogEntry,
    ClearanceDecisionRecord,
    ClinicianNoteRecord,
    FunctionalTest,
    InjuryCase,
    Milestone,
    MilestoneResult,
    Organization,
    OrganizationAuditLogEntry,
    ReturnPlanPhase,
    ReturnPlanTemplate,
    ShareToken,
    SymptomLog,
    User,
    WorkloadSession,
)
from return_play.models import (
    OrganizationCreate,
    PhaseStatus,
    UserCreate,
    UserDeactivateRequest,
    UserRoleUpdate,
)
from return_play.permissions import Permission, assert_permission
from return_play.repositories.demo import DemoSeedService
from return_play.repositories.sqlalchemy_parts.athletes import (
    SqlAlchemyAthleteRepositoryMixin,
)
from return_play.repositories.sqlalchemy_parts.cases import SqlAlchemyCaseRepositoryMixin
from return_play.repositories.sqlalchemy_parts.evidence import (
    SqlAlchemyEvidenceRepositoryMixin,
)
from return_play.repositories.sqlalchemy_parts.readiness import (
    SqlAlchemyReadinessRepositoryMixin,
)
from return_play.repositories.sqlalchemy_parts.shares import SqlAlchemyShareRepositoryMixin
from return_play.repositories.sqlalchemy_parts.templates import (
    SqlAlchemyTemplatePlanRepositoryMixin,
)
from return_play.reports import build_case_report_pdf


class SqlAlchemyWorkflowRepository(
    SqlAlchemyAthleteRepositoryMixin,
    SqlAlchemyCaseRepositoryMixin,
    SqlAlchemyTemplatePlanRepositoryMixin,
    SqlAlchemyEvidenceRepositoryMixin,
    SqlAlchemyReadinessRepositoryMixin,
    SqlAlchemyShareRepositoryMixin,
):
    def __init__(self, session_factory: sessionmaker) -> None:
        self.session_factory = session_factory

    @staticmethod
    def _is_active_phase(phase: dict) -> bool:
        return phase["status"] in {
            PhaseStatus.CURRENT.value,
            PhaseStatus.HELD.value,
        }

    def build_report(self, case_id: str, context: RequestContext) -> bytes:
        assert_permission(context, Permission.GENERATE_REPORTS)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            injury_case = self._get_case(session, case_id, context.organization_id)
            athlete = session.get(Athlete, injury_case.athlete_id)
            readiness = self.get_readiness(case_id, context)
            self._record_audit_event(
                session,
                case_id,
                AuditEventType.REPORT_GENERATED.value,
                context.actor_id,
                {"format": "pdf"},
            )
            self._record_audit_event(
                session,
                case_id,
                AuditEventType.SENSITIVE_EXPORT_READ.value,
                context.actor_id,
                {"export_type": "case_report", "format": "pdf"},
            )
            session.flush()
            audit_events = session.scalars(
                select(AuditLogEntry).where(AuditLogEntry.injury_case_id == case_id)
            ).all()
            case_detail = self._case_detail(session, injury_case)
            audit_metadata = [self._audit_dict(event) for event in audit_events]
            session.commit()
            return build_case_report_pdf(
                {
                    **case_detail,
                    "athlete_name": athlete.name,
                },
                readiness,
                audit_metadata,
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
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._get_case(session, case_id, context.organization_id)
            query = select(AuditLogEntry).where(AuditLogEntry.injury_case_id == case_id)
            if event_type is not None:
                query = query.where(AuditLogEntry.event_type == event_type)
            if actor_id is not None:
                query = query.where(AuditLogEntry.actor_id == actor_id)
            if limit is not None:
                query = query.limit(limit)
            events = session.scalars(query).all()
            return {"items": [self._audit_dict(event) for event in events]}

    def seed_demo(self, context: RequestContext) -> dict:
        assert_permission(context, Permission.SEED_DEMO)
        self._ensure_active_context(context)
        return DemoSeedService(self).seed_demo(context)

    def setup_organization(self, payload: OrganizationCreate, context: RequestContext) -> dict:
        assert_permission(context, Permission.MANAGE_ORGANIZATION)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            organization = session.get(Organization, context.organization_id)
            if organization is None:
                organization = Organization(
                    id=context.organization_id,
                    name=payload.name,
                    timezone=payload.timezone,
                    created_at=self._now(),
                )
                session.add(organization)
            else:
                organization.name = payload.name
                organization.timezone = payload.timezone
            self._ensure_user(session, context.actor_id, context)
            self._record_organization_audit_event(
                session,
                organization.id,
                "organization_configured",
                context.actor_id,
                None,
                {"name": organization.name, "timezone": organization.timezone},
            )
            session.commit()
            return self._organization_dict(organization)

    def invite_user(self, payload: UserCreate, context: RequestContext) -> dict:
        assert_permission(context, Permission.MANAGE_USERS)
        self._ensure_payload_organization(payload.organization_id, context)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._ensure_context_principal(session, context)
            user = User(
                id=self._new_id("user"),
                **payload.model_dump(mode="python"),
                active=True,
                created_at=self._now(),
            )
            session.add(user)
            self._record_organization_audit_event(
                session,
                payload.organization_id,
                "user_invited",
                context.actor_id,
                user.id,
                {"email": user.email, "role": user.role},
            )
            session.commit()
            return self._user_dict(user)

    def update_user_role(
        self,
        user_id: str,
        payload: UserRoleUpdate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_USERS)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            user = self._get_user(session, user_id, context.organization_id)
            previous_role = user.role
            user.role = payload.role.value
            self._record_organization_audit_event(
                session,
                context.organization_id,
                "user_role_updated",
                context.actor_id,
                user.id,
                {"previous_role": previous_role, "new_role": user.role},
            )
            session.commit()
            return self._user_dict(user)

    def deactivate_user(
        self,
        user_id: str,
        payload: UserDeactivateRequest,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_USERS)
        self._ensure_active_context(context)
        if payload.deactivated_by != context.actor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Deactivation actor must match request context.",
            )
        with self.session_factory() as session:
            user = self._get_user(session, user_id, context.organization_id)
            user.active = False
            self._record_organization_audit_event(
                session,
                context.organization_id,
                "user_deactivated",
                context.actor_id,
                user.id,
                {"email": user.email, "role": user.role},
            )
            session.commit()
            return self._user_dict(user)

    def get_organization_audit_log(
        self,
        organization_id: str | None,
        context: RequestContext,
    ) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_ORGANIZATION_AUDIT_LOG)
        self._ensure_requested_organization(organization_id, context)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            events = session.scalars(
                select(OrganizationAuditLogEntry).where(
                    OrganizationAuditLogEntry.organization_id == context.organization_id
                )
            ).all()
            return {"items": [self._organization_audit_dict(event) for event in events]}

    def find_demo_case(self, context: RequestContext) -> dict | None:
        with self.session_factory() as session:
            row = session.execute(
                select(InjuryCase, Athlete)
                .join(Athlete, Athlete.id == InjuryCase.athlete_id)
                .where(
                    InjuryCase.organization_id == context.organization_id,
                    InjuryCase.title == "Left ankle sprain",
                    Athlete.name == "Riley Chen",
                )
            ).first()
            if row is None:
                return None
            injury_case, _athlete = row
            return self._case_dict(injury_case)

    def demo_seed_response(
        self,
        injury_case: dict,
        context: RequestContext,
        *,
        already_seeded: bool,
    ) -> dict:
        with self.session_factory() as session:
            case = self._get_case(session, injury_case["id"], context.organization_id)
            athlete = session.get(Athlete, case.athlete_id)
            current_phase = next(
                (
                    phase
                    for phase in self._case_phases(session, case.id)
                    if self._is_active_phase(phase)
                ),
                None,
            )
            share = session.scalar(
                select(ShareToken).where(
                    ShareToken.injury_case_id == case.id,
                    ShareToken.audience == "coach",
                    ShareToken.revoked_at.is_(None),
                )
            )
            readiness = self.get_readiness(case.id, context)
            return {
                "athlete_id": athlete.id,
                "athlete_name": athlete.name,
                "injury_case_id": case.id,
                "current_phase": current_phase["name"] if current_phase else None,
                "share_token": None if share is not None else None,
                "can_auto_clear": readiness["can_auto_clear"],
                "readiness_signal_count": len(readiness["signals"]),
                "already_seeded": already_seeded,
            }

    def _template_detail(self, session, template: ReturnPlanTemplate) -> dict:
        phases = session.scalars(
            select(ReturnPlanPhase)
            .where(ReturnPlanPhase.template_id == template.id)
            .order_by(ReturnPlanPhase.order_index)
        ).all()
        phase_rows = []
        for phase in phases:
            milestones = session.scalars(
                select(Milestone).where(Milestone.phase_id == phase.id)
            ).all()
            phase_rows.append(
                {
                    **self._template_phase_dict(phase),
                    "milestones": [
                        self._milestone_template_dict(milestone)
                        for milestone in milestones
                    ],
                }
            )
        return {**self._template_dict(template), "phases": phase_rows}

    def _validate_evidence_case(
        self,
        session,
        route_case_id: str,
        payload_case_id: str,
        context: RequestContext,
    ) -> None:
        self._get_case(session, route_case_id, context.organization_id)
        if route_case_id != payload_case_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evidence payload case does not match route.",
            )

    def _get_case(self, session, case_id: str, organization_id: str | None = None) -> InjuryCase:
        injury_case = session.get(InjuryCase, case_id)
        if injury_case is None or (
            organization_id is not None and injury_case.organization_id != organization_id
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Injury case not found.",
            )
        return injury_case

    def _get_template(
        self,
        session,
        template_id: str,
        organization_id: str | None = None,
    ) -> ReturnPlanTemplate:
        template = session.get(ReturnPlanTemplate, template_id)
        if template is None or (
            organization_id is not None and template.organization_id != organization_id
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found.",
            )
        return template

    def _ensure_context_principal(self, session, context: RequestContext) -> None:
        organization = session.get(Organization, context.organization_id)
        if organization is None:
            session.add(
                Organization(
                    id=context.organization_id,
                    name=context.organization_id,
                    timezone="UTC",
                    created_at=self._now(),
                )
            )
        self._ensure_user(session, context.actor_id, context)
        session.flush()

    def _ensure_user(self, session, user_id: str, context: RequestContext) -> None:
        if session.get(User, user_id) is None:
            session.add(
                User(
                    id=user_id,
                    organization_id=context.organization_id,
                    email=f"{user_id}@example.local",
                    name=user_id,
                    role=context.role.value,
                    active=True,
                    created_at=self._now(),
                )
            )
            session.flush()

    def _ensure_active_context(self, context: RequestContext) -> None:
        with self.session_factory() as session:
            user = session.get(User, context.actor_id)
            if user is not None and not user.active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is deactivated.",
                )

    def _get_user(self, session, user_id: str, organization_id: str) -> User:
        user = session.get(User, user_id)
        if user is None or user.organization_id != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return user

    def _record_audit_event(
        self,
        session,
        case_id: str,
        event_type: str,
        actor_id: str | None,
        metadata: dict,
    ) -> AuditLogEntry:
        event = AuditLogEntry(
            id=self._new_id("audit"),
            injury_case_id=case_id,
            event_type=event_type,
            actor_id=actor_id,
            created_at=self._now(),
            metadata_json=metadata,
        )
        session.add(event)
        return event

    def _record_organization_audit_event(
        self,
        session,
        organization_id: str,
        event_type: str,
        actor_id: str | None,
        target_user_id: str | None,
        metadata: dict,
    ) -> OrganizationAuditLogEntry:
        event = OrganizationAuditLogEntry(
            id=self._new_id("org_audit"),
            organization_id=organization_id,
            event_type=event_type,
            actor_id=actor_id,
            target_user_id=target_user_id,
            created_at=self._now(),
            metadata_json=metadata,
        )
        session.add(event)
        return event

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

    @staticmethod
    def _organization_dict(organization: Organization) -> dict[str, Any]:
        return {
            "id": organization.id,
            "name": organization.name,
            "timezone": organization.timezone,
        }

    @staticmethod
    def _user_dict(user: User) -> dict[str, Any]:
        return {
            "id": user.id,
            "organization_id": user.organization_id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "active": user.active,
        }

    @staticmethod
    def _athlete_dict(athlete: Athlete) -> dict[str, Any]:
        return {
            "id": athlete.id,
            "organization_id": athlete.organization_id,
            "name": athlete.name,
            "date_of_birth": athlete.date_of_birth,
            "sport": athlete.sport,
            "position": athlete.position,
            "guardian_contact": athlete.guardian_contact,
            "active": athlete.active,
        }

    @staticmethod
    def _case_dict(injury_case: InjuryCase) -> dict[str, Any]:
        return {
            "id": injury_case.id,
            "organization_id": injury_case.organization_id,
            "athlete_id": injury_case.athlete_id,
            "title": injury_case.title,
            "injury_category": injury_case.injury_category,
            "body_region": injury_case.body_region,
            "side": injury_case.side,
            "date_of_injury": injury_case.date_of_injury,
            "status": injury_case.status,
            "clinician_owner_id": injury_case.clinician_owner_id,
            "summary": injury_case.summary,
            "created_at": injury_case.created_at,
            "updated_at": injury_case.updated_at,
        }

    @staticmethod
    def _template_dict(template: ReturnPlanTemplate) -> dict[str, Any]:
        return {
            "id": template.id,
            "organization_id": template.organization_id,
            "name": template.name,
            "injury_category": template.injury_category,
            "description": template.description,
            "created_by": template.created_by,
            "version": template.version,
            "active": template.active,
        }

    @staticmethod
    def _template_phase_dict(phase: ReturnPlanPhase) -> dict[str, Any]:
        return {
            "id": phase.id,
            "template_id": phase.template_id,
            "name": phase.name,
            "order_index": phase.order_index,
            "objective": phase.objective,
            "minimum_days": phase.minimum_days,
            "exit_summary": phase.exit_summary,
        }

    @staticmethod
    def _milestone_template_dict(milestone: Milestone) -> dict[str, Any]:
        return {
            "id": milestone.id,
            "phase_id": milestone.phase_id,
            "title": milestone.title,
            "kind": milestone.kind,
            "required": milestone.required,
            "instructions": milestone.instructions,
        }

    @staticmethod
    def _milestone_result_dict(result: MilestoneResult) -> dict[str, Any]:
        return {
            "id": result.id,
            "injury_case_id": result.injury_case_id,
            "milestone_id": result.milestone_id,
            "status": result.status,
            "recorded_by": result.recorded_by,
            "recorded_at": result.recorded_at,
            "notes": result.notes,
            "evidence_json": result.evidence_json,
        }

    @staticmethod
    def _note_dict(note: ClinicianNoteRecord) -> dict[str, Any]:
        return {
            "id": note.id,
            "injury_case_id": note.injury_case_id,
            "author_id": note.author_id,
            "body": note.body,
            "created_at": note.created_at,
        }

    @staticmethod
    def _symptom_dict(log: SymptomLog) -> dict[str, Any]:
        return {
            "id": log.id,
            "injury_case_id": log.injury_case_id,
            "athlete_id": log.athlete_id,
            "date": log.date,
            "pain": log.pain,
            "swelling": log.swelling,
            "confidence": log.confidence,
            "notes": log.notes,
        }

    @staticmethod
    def _functional_test_dict(test: FunctionalTest) -> dict[str, Any]:
        return {
            "id": test.id,
            "injury_case_id": test.injury_case_id,
            "name": test.name,
            "test_date": test.test_date,
            "result_value": test.result_value,
            "unit": test.unit,
            "side_to_side_difference_percent": test.side_to_side_difference_percent,
            "passed": test.passed,
            "recorded_by": test.recorded_by,
            "notes": test.notes,
        }

    @staticmethod
    def _workload_dict(item: WorkloadSession) -> dict[str, Any]:
        return {
            "id": item.id,
            "injury_case_id": item.injury_case_id,
            "date": item.date,
            "activity": item.activity,
            "duration_minutes": item.duration_minutes,
            "intensity": item.intensity,
            "symptom_response": item.symptom_response,
            "completed": item.completed,
            "notes": item.notes,
        }

    @staticmethod
    def _clearance_dict(decision: ClearanceDecisionRecord) -> dict[str, Any]:
        return {
            "id": decision.id,
            "injury_case_id": decision.injury_case_id,
            "phase_id": decision.phase_id,
            "decision": decision.decision,
            "decided_by": decision.decided_by,
            "decided_by_role": decision.decided_by_role,
            "decided_at": decision.decided_at,
            "rationale": decision.rationale,
            "restrictions": decision.restrictions,
        }

    @staticmethod
    def _share_dict(share: ShareToken) -> dict[str, Any]:
        return {
            "id": share.id,
            "injury_case_id": share.injury_case_id,
            "audience": share.audience,
            "token_hash": share.token_hash,
            "created_at": share.created_at,
            "expires_at": share.expires_at,
            "revoked_at": share.revoked_at,
            "allowed_activities": share.allowed_activities,
            "restricted_activities": share.restricted_activities,
            "clinician_note": share.clinician_note,
            "next_review_date": share.next_review_date,
        }

    def _get_active_share_by_token(self, session, token: str) -> ShareToken:
        share = session.scalar(
            select(ShareToken).where(ShareToken.token_hash == self._hash_token(token))
        )
        if share is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share token not found.",
            )
        if share.revoked_at is not None:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Share token has been revoked.",
            )
        if self._to_naive_utc(share.expires_at) <= self._now():
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Share token has expired.",
            )
        return share

    @staticmethod
    def _audit_dict(event: AuditLogEntry) -> dict[str, Any]:
        return {
            "id": event.id,
            "injury_case_id": event.injury_case_id,
            "event_type": event.event_type,
            "actor_id": event.actor_id,
            "created_at": event.created_at,
            "metadata_json": event.metadata_json,
        }

    @staticmethod
    def _organization_audit_dict(event: OrganizationAuditLogEntry) -> dict[str, Any]:
        return {
            "id": event.id,
            "organization_id": event.organization_id,
            "event_type": event.event_type,
            "actor_id": event.actor_id,
            "target_user_id": event.target_user_id,
            "created_at": event.created_at,
            "metadata_json": event.metadata_json,
        }

    @staticmethod
    def _hash_token(token: str) -> str:
        return sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}_{uuid4().hex}"

    @staticmethod
    def _now() -> datetime:
        return datetime.utcnow()

    @staticmethod
    def _to_naive_utc(value: datetime) -> datetime:
        # Postgres returns tz-aware datetimes for timestamptz columns while
        # SQLite returns naive ones; normalize to naive UTC so comparisons with
        # _now() behave the same on both engines.
        if value.tzinfo is None:
            return value
        return value.astimezone(timezone.utc).replace(tzinfo=None)
