from __future__ import annotations

from fastapi import HTTPException, status

from return_play.auth import RequestContext
from return_play.models import FunctionalTestCreate, SymptomLogCreate, WorkloadSessionCreate
from return_play.permissions import Permission, assert_permission


class InMemoryEvidenceRepositoryMixin:
    def create_symptom_log(
        self,
        case_id: str,
        payload: SymptomLogCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_EVIDENCE)
        self._ensure_active_user(context)
        self._validate_evidence_case(case_id, payload.injury_case_id, context)
        athlete = self.athletes.get(payload.athlete_id)
        if athlete is None or athlete["organization_id"] != context.organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Athlete not found.",
            )
        symptom_log = payload.model_dump(mode="json")
        symptom_log["id"] = self._new_id("symptom")
        symptom_log["recorded_at"] = self._now()
        self.symptom_logs.setdefault(case_id, []).append(symptom_log)
        self._record_audit_event(
            case_id,
            "symptom_logged",
            context.actor_id,
            {"symptom_log_id": symptom_log["id"], "pain": symptom_log["pain"]},
        )
        return symptom_log

    def list_symptom_logs(self, case_id: str, context: RequestContext) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_EVIDENCE)
        self._ensure_active_user(context)
        self._get_case(case_id, context.organization_id)
        return {"items": self.symptom_logs.get(case_id, [])}

    def create_functional_test(
        self,
        case_id: str,
        payload: FunctionalTestCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_EVIDENCE)
        self._ensure_active_user(context)
        self._validate_evidence_case(case_id, payload.injury_case_id, context)
        functional_test = payload.model_dump(mode="json")
        functional_test["id"] = self._new_id("functional_test")
        functional_test["recorded_at"] = self._now()
        self.functional_tests.setdefault(case_id, []).append(functional_test)
        self._record_audit_event(
            case_id,
            "functional_test_logged",
            payload.recorded_by,
            {
                "functional_test_id": functional_test["id"],
                "passed": functional_test["passed"],
            },
        )
        return functional_test

    def list_functional_tests(
        self,
        case_id: str,
        context: RequestContext,
    ) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_EVIDENCE)
        self._ensure_active_user(context)
        self._get_case(case_id, context.organization_id)
        return {"items": self.functional_tests.get(case_id, [])}

    def create_workload_session(
        self,
        case_id: str,
        payload: WorkloadSessionCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_EVIDENCE)
        self._ensure_active_user(context)
        self._validate_evidence_case(case_id, payload.injury_case_id, context)
        workload_session = payload.model_dump(mode="json")
        workload_session["id"] = self._new_id("workload")
        workload_session["recorded_at"] = self._now()
        self.workload_sessions.setdefault(case_id, []).append(workload_session)
        self._record_audit_event(
            case_id,
            "workload_session_logged",
            context.actor_id,
            {
                "workload_session_id": workload_session["id"],
                "completed": workload_session["completed"],
            },
        )
        return workload_session

    def list_workload_sessions(
        self,
        case_id: str,
        context: RequestContext,
    ) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_EVIDENCE)
        self._ensure_active_user(context)
        self._get_case(case_id, context.organization_id)
        return {"items": self.workload_sessions.get(case_id, [])}
