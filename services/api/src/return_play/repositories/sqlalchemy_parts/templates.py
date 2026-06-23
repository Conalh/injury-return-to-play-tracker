from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select

from return_play.auth import RequestContext
from return_play.db import CasePhaseStatus, Milestone, ReturnPlanPhase, ReturnPlanTemplate
from return_play.models import (
    ApplyTemplateRequest,
    PhaseStatus,
    ReturnPlanTemplateWithPhasesCreate,
)
from return_play.permissions import Permission, assert_permission


class SqlAlchemyTemplatePlanRepositoryMixin:
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
            template, phase_rows = self._create_template_rows(session, payload)
            session.commit()
            return {**self._template_dict(template), "phases": phase_rows}

    def _create_template_rows(
        self,
        session,
        payload: ReturnPlanTemplateWithPhasesCreate,
        version: int | None = None,
        active: bool | None = None,
    ) -> tuple[ReturnPlanTemplate, list[dict]]:
        values = payload.model_dump(mode="python", exclude={"phases"})
        if version is not None:
            values["version"] = version
        if active is not None:
            values["active"] = active
        template = ReturnPlanTemplate(
            id=self._new_id("template"),
            **values,
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
                session.flush()
                milestone_rows.append(self._milestone_template_dict(milestone))
            phase_rows.append(
                {
                    **self._template_phase_dict(phase),
                    "milestones": milestone_rows,
                }
            )

        return template, phase_rows

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

    def get_template_detail(self, template_id: str, context: RequestContext) -> dict:
        assert_permission(context, Permission.READ_TEMPLATES)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            template = self._get_template(session, template_id, context.organization_id)
            return self._template_detail(session, template)

    def update_template(
        self,
        template_id: str,
        payload: ReturnPlanTemplateWithPhasesCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_TEMPLATES)
        self._ensure_active_context(context)
        self._ensure_payload_organization(payload.organization_id, context)
        with self.session_factory() as session:
            self._ensure_context_principal(session, context)
            self._ensure_user(session, payload.created_by, context)
            previous = self._get_template(session, template_id, context.organization_id)
            previous.active = False
            template, phase_rows = self._create_template_rows(
                session,
                payload,
                version=previous.version + 1,
                active=True,
            )
            session.commit()
            return {**self._template_dict(template), "phases": phase_rows}

    def archive_template(self, template_id: str, context: RequestContext) -> dict:
        assert_permission(context, Permission.MANAGE_TEMPLATES)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            template = self._get_template(session, template_id, context.organization_id)
            template.active = False
            session.commit()
            return self._template_dict(template)

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
            if not template.active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Template is archived.",
                )
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
