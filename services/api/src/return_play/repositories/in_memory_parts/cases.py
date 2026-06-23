from __future__ import annotations

from fastapi import HTTPException, status

from return_play.auth import RequestContext
from return_play.models import ClinicianNoteCreate, InjuryCaseCreate, MilestoneResultUpdate
from return_play.permissions import Permission, assert_permission


class InMemoryCaseRepositoryMixin:
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
