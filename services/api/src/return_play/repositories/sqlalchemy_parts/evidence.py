from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select

from return_play.auth import RequestContext
from return_play.db import Athlete, FunctionalTest, SymptomLog, WorkloadSession
from return_play.models import FunctionalTestCreate, SymptomLogCreate, WorkloadSessionCreate
from return_play.permissions import Permission, assert_permission


class SqlAlchemyEvidenceRepositoryMixin:
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
            self._record_audit_event(
                session,
                case_id,
                "symptom_logged",
                context.actor_id,
                {"symptom_log_id": symptom_log.id, "pain": symptom_log.pain},
            )
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
            self._record_audit_event(
                session,
                case_id,
                "functional_test_logged",
                payload.recorded_by,
                {
                    "functional_test_id": functional_test.id,
                    "passed": functional_test.passed,
                },
            )
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
            self._record_audit_event(
                session,
                case_id,
                "workload_session_logged",
                context.actor_id,
                {
                    "workload_session_id": workload_session.id,
                    "completed": workload_session.completed,
                },
            )
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
