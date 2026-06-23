from __future__ import annotations

from fastapi import HTTPException, status

from return_play.auth import RequestContext
from return_play.models import (
    ClearanceDecision,
    ClearanceDecisionCreate,
    InjuryCaseStatus,
    PhaseStatus,
)
from return_play.permissions import Permission, assert_permission
from return_play.readiness import build_readiness


class InMemoryReadinessRepositoryMixin:
    def get_readiness(self, case_id: str, context: RequestContext) -> dict:
        assert_permission(context, Permission.READ_READINESS)
        self._ensure_active_user(context)
        self._get_case(case_id, context.organization_id)
        phases = self.case_plans.get(case_id, [])
        current_phase = next(
            (phase for phase in phases if self._is_active_phase(phase)),
            None,
        )
        return build_readiness(
            injury_case_id=case_id,
            current_phase=current_phase,
            symptom_logs=self.symptom_logs.get(case_id, []),
            workload_sessions=self.workload_sessions.get(case_id, []),
            clearance_decisions=self.clearance_decisions.get(case_id, []),
        )

    def create_clearance_decision(
        self,
        case_id: str,
        payload: ClearanceDecisionCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.RECORD_CLEARANCE_DECISIONS)
        self._ensure_active_user(context)
        self._validate_evidence_case(case_id, payload.injury_case_id, context)
        if payload.decided_by != context.actor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Clearance decision actor must match request context.",
            )

        decision = payload.model_dump(mode="json")
        decision["id"] = self._new_id("clearance")
        decision["decided_at"] = self._now()
        self._apply_clearance_decision(case_id, decision)
        self.clearance_decisions.setdefault(case_id, []).append(decision)
        self._record_audit_event(
            case_id,
            "clearance_decision_recorded",
            context.actor_id,
            {
                "decision": decision["decision"],
                "decided_by_role": decision["decided_by_role"],
                "phase_id": decision["phase_id"],
            },
        )
        return decision

    def _apply_clearance_decision(self, case_id: str, decision: dict) -> None:
        phases = self.case_plans.get(case_id, [])
        phase_index = next(
            (
                index
                for index, phase in enumerate(phases)
                if phase["id"] == decision["phase_id"]
            ),
            None,
        )
        if phase_index is None and phases:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case phase not found.",
            )

        match decision["decision"]:
            case ClearanceDecision.HOLD.value:
                if phase_index is not None:
                    phases[phase_index]["status"] = PhaseStatus.HELD.value
            case ClearanceDecision.ADVANCE.value:
                if phase_index is None or phase_index + 1 >= len(phases):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No next phase is available to advance.",
                    )
                phases[phase_index]["status"] = PhaseStatus.PASSED.value
                phases[phase_index + 1]["status"] = PhaseStatus.CURRENT.value
            case ClearanceDecision.CLEAR_FULL.value:
                for phase in phases:
                    phase["status"] = PhaseStatus.PASSED.value
                self.injury_cases[case_id]["status"] = InjuryCaseStatus.CLEARED.value
            case ClearanceDecision.CLOSE_CASE.value:
                self.injury_cases[case_id]["status"] = InjuryCaseStatus.CLOSED.value
