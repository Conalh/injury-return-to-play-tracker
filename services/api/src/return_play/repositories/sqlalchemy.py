from __future__ import annotations

from datetime import datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from return_play.auth import RequestContext
from return_play.db import (
    Athlete,
    AuditLogEntry,
    CasePhaseStatus,
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
    ApplyTemplateRequest,
    AthleteCreate,
    ClearanceDecisionCreate,
    ClinicianNoteCreate,
    FunctionalTestCreate,
    InjuryCaseCreate,
    MilestoneResultStatus,
    MilestoneResultUpdate,
    OrganizationCreate,
    PhaseStatus,
    ReturnPlanTemplateWithPhasesCreate,
    ShareTokenCreate,
    ShareTokenRevoke,
    SymptomLogCreate,
    UserCreate,
    UserDeactivateRequest,
    UserRoleUpdate,
    WorkloadSessionCreate,
)
from return_play.permissions import Permission, assert_permission
from return_play.readiness import build_readiness
from return_play.repositories.demo import DemoSeedService
from return_play.reports import build_case_report_pdf


class SqlAlchemyWorkflowRepository:
    def __init__(self, session_factory: sessionmaker) -> None:
        self.session_factory = session_factory

    def create_athlete(self, payload: AthleteCreate, context: RequestContext) -> dict:
        assert_permission(context, Permission.MANAGE_ATHLETES)
        self._ensure_active_context(context)
        self._ensure_payload_organization(payload.organization_id, context)
        with self.session_factory() as session:
            self._ensure_context_principal(session, context)
            athlete = Athlete(
                id=self._new_id("athlete"),
                **payload.model_dump(mode="python"),
            )
            session.add(athlete)
            session.commit()
            return self._athlete_dict(athlete)

    def list_athletes(
        self,
        context: RequestContext,
        organization_id: str | None = None,
    ) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_ATHLETES)
        self._ensure_requested_organization(organization_id, context)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            athletes = session.scalars(
                select(Athlete).where(Athlete.organization_id == context.organization_id)
            ).all()
            return {"items": [self._athlete_dict(athlete) for athlete in athletes]}

    def create_injury_case(self, payload: InjuryCaseCreate, context: RequestContext) -> dict:
        assert_permission(context, Permission.MANAGE_CLINICAL_CASES)
        self._ensure_active_context(context)
        self._ensure_payload_organization(payload.organization_id, context)
        with self.session_factory() as session:
            self._ensure_context_principal(session, context)
            athlete = session.get(Athlete, payload.athlete_id)
            if athlete is None or athlete.organization_id != context.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Athlete not found.",
                )
            self._ensure_user(session, payload.clinician_owner_id, context)
            now = self._now()
            injury_case = InjuryCase(
                id=self._new_id("case"),
                created_at=now,
                updated_at=now,
                **payload.model_dump(mode="python"),
            )
            session.add(injury_case)
            session.commit()
            return self._case_dict(injury_case)

    def get_injury_case_detail(self, case_id: str, context: RequestContext) -> dict:
        assert_permission(context, Permission.READ_CLINICAL_CASES)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            injury_case = self._get_case(session, case_id, context.organization_id)
            return self._case_detail(session, injury_case)

    def create_template(
        self,
        payload: ReturnPlanTemplateWithPhasesCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_TEMPLATES)
        self._ensure_active_context(context)
        self._ensure_payload_organization(payload.organization_id, context)
        with self.session_factory() as session:
            self._ensure_context_principal(session, context)
            self._ensure_user(session, payload.created_by, context)
            template = ReturnPlanTemplate(
                id=self._new_id("template"),
                **payload.model_dump(mode="python", exclude={"phases"}),
            )
            session.add(template)
            session.flush()

            phase_rows = []
            for phase_payload in sorted(payload.phases, key=lambda phase: phase.order_index):
                phase = ReturnPlanPhase(
                    id=self._new_id("phase"),
                    template_id=template.id,
                    **phase_payload.model_dump(mode="python", exclude={"milestones"}),
                )
                session.add(phase)
                session.flush()
                milestone_rows = []
                for milestone_payload in phase_payload.milestones:
                    milestone = Milestone(
                        id=self._new_id("milestone"),
                        phase_id=phase.id,
                        **milestone_payload.model_dump(mode="python"),
                    )
                    session.add(milestone)
                    milestone_rows.append(self._milestone_template_dict(milestone))
                phase_rows.append(
                    {
                        **self._template_phase_dict(phase),
                        "milestones": milestone_rows,
                    }
                )

            session.commit()
            return {**self._template_dict(template), "phases": phase_rows}

    def list_templates(
        self,
        context: RequestContext,
        organization_id: str | None = None,
    ) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_TEMPLATES)
        self._ensure_active_context(context)
        self._ensure_requested_organization(organization_id, context)
        with self.session_factory() as session:
            templates = session.scalars(
                select(ReturnPlanTemplate).where(
                    ReturnPlanTemplate.organization_id == context.organization_id
                )
            ).all()
            return {"items": [self._template_dict(template) for template in templates]}

    def apply_template(
        self,
        case_id: str,
        payload: ApplyTemplateRequest,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_CLINICAL_CASES)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._get_case(session, case_id, context.organization_id)
            template = self._get_template(session, payload.template_id, context.organization_id)
            phases = session.scalars(
                select(ReturnPlanPhase)
                .where(ReturnPlanPhase.template_id == template.id)
                .order_by(ReturnPlanPhase.order_index)
            ).all()
            applied_phases = []
            for index, phase in enumerate(phases):
                case_phase = CasePhaseStatus(
                    id=self._new_id("case_phase"),
                    injury_case_id=case_id,
                    phase_id=phase.id,
                    status=(
                        PhaseStatus.CURRENT.value
                        if index == 0
                        else PhaseStatus.LOCKED.value
                    ),
                )
                session.add(case_phase)
                session.flush()
                applied_phases.append(self._case_phase_dict(session, case_phase))
            session.commit()
            return {
                "injury_case_id": case_id,
                "template_id": template.id,
                "phases": applied_phases,
            }

    def list_case_phases(self, case_id: str, context: RequestContext) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_CLINICAL_CASES)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._get_case(session, case_id, context.organization_id)
            return {"items": self._case_phases(session, case_id)}

    def update_milestone(
        self,
        case_id: str,
        milestone_id: str,
        payload: MilestoneResultUpdate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_CLINICAL_CASES)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._get_case(session, case_id, context.organization_id)
            milestone = session.get(Milestone, milestone_id)
            if milestone is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Milestone not found for injury case.",
                )
            self._ensure_user(session, payload.recorded_by, context)
            result = session.scalar(
                select(MilestoneResult).where(
                    MilestoneResult.injury_case_id == case_id,
                    MilestoneResult.milestone_id == milestone_id,
                )
            )
            if result is None:
                result = MilestoneResult(
                    id=self._new_id("milestone_result"),
                    injury_case_id=case_id,
                    milestone_id=milestone_id,
                    recorded_by=payload.recorded_by,
                    recorded_at=self._now(),
                    status=payload.status.value,
                    notes=payload.notes,
                    evidence_json=payload.evidence_json,
                )
                session.add(result)
            else:
                result.status = payload.status.value
                result.recorded_by = payload.recorded_by
                result.recorded_at = self._now()
                result.notes = payload.notes
                result.evidence_json = payload.evidence_json
            session.commit()
            return self._milestone_result_dict(result)

    def create_note(
        self,
        case_id: str,
        payload: ClinicianNoteCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_CLINICAL_CASES)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._get_case(session, case_id, context.organization_id)
            self._ensure_user(session, payload.author_id, context)
            note = ClinicianNoteRecord(
                id=self._new_id("note"),
                injury_case_id=case_id,
                created_at=self._now(),
                **payload.model_dump(mode="python"),
            )
            session.add(note)
            session.commit()
            return self._note_dict(note)

    def create_symptom_log(
        self,
        case_id: str,
        payload: SymptomLogCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_EVIDENCE)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._validate_evidence_case(session, case_id, payload.injury_case_id, context)
            athlete = session.get(Athlete, payload.athlete_id)
            if athlete is None or athlete.organization_id != context.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Athlete not found.",
                )
            symptom_log = SymptomLog(
                id=self._new_id("symptom"),
                **payload.model_dump(mode="python"),
            )
            session.add(symptom_log)
            session.commit()
            return self._symptom_dict(symptom_log)

    def list_symptom_logs(self, case_id: str, context: RequestContext) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_EVIDENCE)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._get_case(session, case_id, context.organization_id)
            logs = session.scalars(
                select(SymptomLog).where(SymptomLog.injury_case_id == case_id)
            ).all()
            return {"items": [self._symptom_dict(log) for log in logs]}

    def create_functional_test(
        self,
        case_id: str,
        payload: FunctionalTestCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_EVIDENCE)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._validate_evidence_case(session, case_id, payload.injury_case_id, context)
            self._ensure_user(session, payload.recorded_by, context)
            functional_test = FunctionalTest(
                id=self._new_id("functional_test"),
                **payload.model_dump(mode="python"),
            )
            session.add(functional_test)
            session.commit()
            return self._functional_test_dict(functional_test)

    def list_functional_tests(
        self,
        case_id: str,
        context: RequestContext,
    ) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_EVIDENCE)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._get_case(session, case_id, context.organization_id)
            tests = session.scalars(
                select(FunctionalTest).where(FunctionalTest.injury_case_id == case_id)
            ).all()
            return {"items": [self._functional_test_dict(test) for test in tests]}

    def create_workload_session(
        self,
        case_id: str,
        payload: WorkloadSessionCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_EVIDENCE)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._validate_evidence_case(session, case_id, payload.injury_case_id, context)
            workload_session = WorkloadSession(
                id=self._new_id("workload"),
                **payload.model_dump(mode="python"),
            )
            session.add(workload_session)
            session.commit()
            return self._workload_dict(workload_session)

    def list_workload_sessions(
        self,
        case_id: str,
        context: RequestContext,
    ) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_EVIDENCE)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._get_case(session, case_id, context.organization_id)
            sessions = session.scalars(
                select(WorkloadSession).where(WorkloadSession.injury_case_id == case_id)
            ).all()
            return {"items": [self._workload_dict(item) for item in sessions]}

    def get_readiness(self, case_id: str, context: RequestContext) -> dict:
        assert_permission(context, Permission.READ_READINESS)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._get_case(session, case_id, context.organization_id)
            current_phase = next(
                (
                    phase
                    for phase in self._case_phases(session, case_id)
                    if phase["status"] == PhaseStatus.CURRENT.value
                ),
                None,
            )
            symptom_logs = [
                self._symptom_dict(log)
                for log in session.scalars(
                    select(SymptomLog).where(SymptomLog.injury_case_id == case_id)
                ).all()
            ]
            workload_sessions = [
                self._workload_dict(item)
                for item in session.scalars(
                    select(WorkloadSession).where(WorkloadSession.injury_case_id == case_id)
                ).all()
            ]
            decisions = [
                self._clearance_dict(item)
                for item in session.scalars(
                    select(ClearanceDecisionRecord).where(
                        ClearanceDecisionRecord.injury_case_id == case_id
                    )
                ).all()
            ]
            return build_readiness(
                injury_case_id=case_id,
                current_phase=current_phase,
                symptom_logs=symptom_logs,
                workload_sessions=workload_sessions,
                clearance_decisions=decisions,
            )

    def create_clearance_decision(
        self,
        case_id: str,
        payload: ClearanceDecisionCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.RECORD_CLEARANCE_DECISIONS)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._validate_evidence_case(session, case_id, payload.injury_case_id, context)
            if payload.decided_by != context.actor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Clearance decision actor must match request context.",
                )
            self._ensure_user(session, payload.decided_by, context)
            decision = ClearanceDecisionRecord(
                id=self._new_id("clearance"),
                decided_at=self._now(),
                **payload.model_dump(mode="python"),
            )
            session.add(decision)
            session.flush()
            self._record_audit_event(
                session,
                case_id,
                "clearance_decision_recorded",
                context.actor_id,
                {
                    "decision": decision.decision,
                    "decided_by_role": decision.decided_by_role,
                    "phase_id": decision.phase_id,
                },
            )
            session.commit()
            return self._clearance_dict(decision)

    def create_share(
        self,
        case_id: str,
        payload: ShareTokenCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_SHARES)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._validate_evidence_case(session, case_id, payload.injury_case_id, context)
            raw_token = token_urlsafe(24)
            now = self._now()
            share = ShareToken(
                id=self._new_id("share"),
                token_hash=self._hash_token(raw_token),
                created_at=now,
                expires_at=now + timedelta(days=payload.expires_in_days),
                revoked_at=None,
                injury_case_id=payload.injury_case_id,
                audience=payload.audience.value,
                allowed_activities=payload.allowed_activities,
                restricted_activities=payload.restricted_activities,
                clinician_note=payload.clinician_note,
                next_review_date=payload.next_review_date,
            )
            session.add(share)
            session.flush()
            self._record_audit_event(
                session,
                case_id,
                "share_created",
                context.actor_id,
                {"audience": payload.audience.value, "share_id": share.id},
            )
            session.commit()
            return {**self._share_dict(share), "token": raw_token}

    def get_share(self, token: str) -> dict:
        with self.session_factory() as session:
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
            if share.expires_at <= self._now():
                raise HTTPException(
                    status_code=status.HTTP_410_GONE,
                    detail="Share token has expired.",
                )
            injury_case = session.get(InjuryCase, share.injury_case_id)
            athlete = session.get(Athlete, injury_case.athlete_id)
            current_phase = next(
                (
                    phase
                    for phase in self._case_phases(session, injury_case.id)
                    if phase["status"] == PhaseStatus.CURRENT.value
                ),
                None,
            )
            return {
                "audience": share.audience,
                "athlete_name": athlete.name,
                "sport": athlete.sport,
                "injury_title": injury_case.title,
                "current_phase": current_phase["name"] if current_phase else None,
                "participation_status": "Modified participation",
                "allowed_activities": share.allowed_activities,
                "restricted_activities": share.restricted_activities,
                "next_review_date": share.next_review_date,
                "clearance_status": (
                    "Awaiting named clinician decision. "
                    "This shared view is not medical clearance."
                ),
                "clinician_note": share.clinician_note,
            }

    def revoke_share(
        self,
        token: str,
        payload: ShareTokenRevoke,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_SHARES)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            share = session.scalar(
                select(ShareToken).where(ShareToken.token_hash == self._hash_token(token))
            )
            if share is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Share token not found.",
                )
            self._get_case(session, share.injury_case_id, context.organization_id)
            if payload.revoked_by != context.actor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Revocation actor must match request context.",
                )
            if share.revoked_at is None:
                share.revoked_at = self._now()
                self._record_audit_event(
                    session,
                    share.injury_case_id,
                    "share_revoked",
                    context.actor_id,
                    {"audience": share.audience, "share_id": share.id},
                )
            session.commit()
            return self._share_dict(share)

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
                "report_generated",
                context.actor_id,
                {"format": "pdf"},
            )
            session.commit()
            return build_case_report_pdf(
                {
                    **self._case_dict(injury_case),
                    "athlete_name": athlete.name,
                },
                readiness,
            )

    def get_audit_log(self, case_id: str, context: RequestContext) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_AUDIT_LOG)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._get_case(session, case_id, context.organization_id)
            events = session.scalars(
                select(AuditLogEntry).where(AuditLogEntry.injury_case_id == case_id)
            ).all()
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
                    if phase["status"] == PhaseStatus.CURRENT.value
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

    def _case_detail(self, session, injury_case: InjuryCase) -> dict:
        return {
            **self._case_dict(injury_case),
            "phases": self._case_phases(session, injury_case.id),
            "current_phase": next(
                (
                    phase
                    for phase in self._case_phases(session, injury_case.id)
                    if phase["status"] == PhaseStatus.CURRENT.value
                ),
                None,
            ),
            "notes": [
                self._note_dict(note)
                for note in session.scalars(
                    select(ClinicianNoteRecord).where(
                        ClinicianNoteRecord.injury_case_id == injury_case.id
                    )
                ).all()
            ],
            "symptom_logs": [
                self._symptom_dict(log)
                for log in session.scalars(
                    select(SymptomLog).where(SymptomLog.injury_case_id == injury_case.id)
                ).all()
            ],
            "functional_tests": [
                self._functional_test_dict(test)
                for test in session.scalars(
                    select(FunctionalTest).where(
                        FunctionalTest.injury_case_id == injury_case.id
                    )
                ).all()
            ],
            "workload_sessions": [
                self._workload_dict(item)
                for item in session.scalars(
                    select(WorkloadSession).where(
                        WorkloadSession.injury_case_id == injury_case.id
                    )
                ).all()
            ],
            "clearance_decisions": [
                self._clearance_dict(item)
                for item in session.scalars(
                    select(ClearanceDecisionRecord).where(
                        ClearanceDecisionRecord.injury_case_id == injury_case.id
                    )
                ).all()
            ],
        }

    def _case_phases(self, session, case_id: str) -> list[dict]:
        case_phases = session.scalars(
            select(CasePhaseStatus).where(CasePhaseStatus.injury_case_id == case_id)
        ).all()
        return [self._case_phase_dict(session, case_phase) for case_phase in case_phases]

    def _case_phase_dict(self, session, case_phase: CasePhaseStatus) -> dict:
        phase = session.get(ReturnPlanPhase, case_phase.phase_id)
        milestones = session.scalars(
            select(Milestone).where(Milestone.phase_id == phase.id)
        ).all()
        return {
            "id": case_phase.id,
            "template_phase_id": phase.id,
            "name": phase.name,
            "order_index": phase.order_index,
            "objective": phase.objective,
            "minimum_days": phase.minimum_days,
            "exit_summary": phase.exit_summary,
            "status": case_phase.status,
            "clinician_note": case_phase.clinician_note,
            "milestones": [
                self._case_milestone_dict(session, case_phase.injury_case_id, milestone)
                for milestone in milestones
            ],
        }

    def _case_milestone_dict(self, session, case_id: str, milestone: Milestone) -> dict:
        result = session.scalar(
            select(MilestoneResult).where(
                MilestoneResult.injury_case_id == case_id,
                MilestoneResult.milestone_id == milestone.id,
            )
        )
        return {
            "id": milestone.id,
            "template_milestone_id": milestone.id,
            "title": milestone.title,
            "kind": milestone.kind,
            "required": milestone.required,
            "instructions": milestone.instructions,
            "status": (
                result.status if result is not None else MilestoneResultStatus.NOT_STARTED.value
            ),
            "recorded_by": result.recorded_by if result is not None else None,
            "recorded_at": result.recorded_at if result is not None else None,
            "notes": result.notes if result is not None else None,
            "evidence_json": result.evidence_json if result is not None else {},
        }

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
