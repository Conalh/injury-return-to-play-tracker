from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select

from return_play.auth import RequestContext
from return_play.db import (
    Athlete,
    CasePhaseStatus,
    ClearanceDecisionRecord,
    ClinicianNoteRecord,
    FunctionalTest,
    InjuryCase,
    Milestone,
    MilestoneResult,
    ReturnPlanPhase,
    SymptomLog,
    WorkloadSession,
)
from return_play.models import (
    ClinicianNoteCreate,
    InjuryCaseCreate,
    MilestoneResultStatus,
    MilestoneResultUpdate,
)
from return_play.permissions import Permission, assert_permission


class SqlAlchemyCaseRepositoryMixin:
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

    def list_injury_cases(
        self,
        context: RequestContext,
        organization_id: str | None = None,
    ) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_CLINICAL_CASES)
        self._ensure_active_context(context)
        self._ensure_requested_organization(organization_id, context)
        with self.session_factory() as session:
            injury_cases = session.scalars(
                select(InjuryCase).where(InjuryCase.organization_id == context.organization_id)
            ).all()
            return {"items": [self._case_dict(injury_case) for injury_case in injury_cases]}

    def get_injury_case_detail(self, case_id: str, context: RequestContext) -> dict:
        assert_permission(context, Permission.READ_CLINICAL_CASES)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            injury_case = self._get_case(session, case_id, context.organization_id)
            return self._case_detail(session, injury_case)

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
            self._record_audit_event(
                session,
                case_id,
                "milestone_evidence_recorded",
                payload.recorded_by,
                {
                    "milestone_id": milestone_id,
                    "status": payload.status.value,
                },
            )
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

    def _case_detail(self, session, injury_case: InjuryCase) -> dict:
        return {
            **self._case_dict(injury_case),
            "phases": self._case_phases(session, injury_case.id),
            "current_phase": next(
                (
                    phase
                    for phase in self._case_phases(session, injury_case.id)
                    if self._is_active_phase(phase)
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
