from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select

from return_play.auth import RequestContext
from return_play.db import (
    CasePhaseStatus,
    ClearanceDecisionRecord,
    ReturnPlanPhase,
    SymptomLog,
    WorkloadSession,
)
from return_play.models import (
    ClearanceDecision,
    ClearanceDecisionCreate,
    InjuryCaseStatus,
    PhaseStatus,
)
from return_play.permissions import Permission, assert_permission
from return_play.readiness import build_readiness


class SqlAlchemyReadinessRepositoryMixin:
    def get_readiness(self, case_id: str, context: RequestContext) -> dict:
        assert_permission(context, Permission.READ_READINESS)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._get_case(session, case_id, context.organization_id)
            current_phase = next(
                (
                    phase
                    for phase in self._case_phases(session, case_id)
                    if self._is_active_phase(phase)
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
            self._apply_clearance_decision(session, case_id, decision)
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

    def _apply_clearance_decision(
        self,
        session,
        case_id: str,
        decision: ClearanceDecisionRecord,
    ) -> None:
        phases = session.scalars(
            select(CasePhaseStatus).where(CasePhaseStatus.injury_case_id == case_id)
        ).all()
        phases = sorted(
            phases,
            key=lambda item: session.get(ReturnPlanPhase, item.phase_id).order_index,
        )
        phase_index = next(
            (
                index
                for index, phase in enumerate(phases)
                if phase.id == decision.phase_id
            ),
            None,
        )
        if phase_index is None and phases:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case phase not found.",
            )

        match decision.decision:
            case ClearanceDecision.HOLD.value:
                if phase_index is not None:
                    phases[phase_index].status = PhaseStatus.HELD.value
            case ClearanceDecision.ADVANCE.value:
                if phase_index is None or phase_index + 1 >= len(phases):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No next phase is available to advance.",
                    )
                phases[phase_index].status = PhaseStatus.PASSED.value
                phases[phase_index + 1].status = PhaseStatus.CURRENT.value
            case ClearanceDecision.CLEAR_FULL.value:
                for phase in phases:
                    phase.status = PhaseStatus.PASSED.value
                injury_case = self._get_case(session, case_id)
                injury_case.status = InjuryCaseStatus.CLEARED.value
            case ClearanceDecision.CLOSE_CASE.value:
                injury_case = self._get_case(session, case_id)
                injury_case.status = InjuryCaseStatus.CLOSED.value
