from __future__ import annotations

from fastapi import HTTPException, status

from return_play.auth import RequestContext
from return_play.models import (
    ApplyTemplateRequest,
    MilestoneResultStatus,
    PhaseStatus,
    ReturnPlanTemplateWithPhasesCreate,
)
from return_play.permissions import Permission, assert_permission


class InMemoryTemplatePlanRepositoryMixin:
    def create_template(
        self,
        payload: ReturnPlanTemplateWithPhasesCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_TEMPLATES)
        self._ensure_active_user(context)
        self._ensure_payload_organization(payload.organization_id, context)
        template = self._build_template(payload)
        self.templates[template["id"]] = template
        return template

    def _build_template(
        self,
        payload: ReturnPlanTemplateWithPhasesCreate,
        version: int | None = None,
        active: bool | None = None,
    ) -> dict:
        template = payload.model_dump(mode="json", exclude={"phases"})
        template["id"] = self._new_id("template")
        if version is not None:
            template["version"] = version
        if active is not None:
            template["active"] = active
        template["phases"] = []

        for phase_payload in sorted(payload.phases, key=lambda phase: phase.order_index):
            phase = phase_payload.model_dump(mode="json", exclude={"milestones"})
            phase["id"] = self._new_id("phase")
            phase["template_id"] = template["id"]
            phase["milestones"] = []
            for milestone_payload in phase_payload.milestones:
                milestone = milestone_payload.model_dump(mode="json")
                milestone["id"] = self._new_id("milestone")
                milestone["phase_id"] = phase["id"]
                phase["milestones"].append(milestone)
            template["phases"].append(phase)

        return template

    def list_templates(
        self,
        context: RequestContext,
        organization_id: str | None = None,
    ) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_TEMPLATES)
        self._ensure_active_user(context)
        self._ensure_requested_organization(organization_id, context)
        templates = list(self.templates.values())
        templates = [
            template
            for template in templates
            if template["organization_id"] == context.organization_id
        ]
        return {"items": templates}

    def get_template_detail(self, template_id: str, context: RequestContext) -> dict:
        assert_permission(context, Permission.READ_TEMPLATES)
        self._ensure_active_user(context)
        return self._get_template(template_id, context.organization_id)

    def update_template(
        self,
        template_id: str,
        payload: ReturnPlanTemplateWithPhasesCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_TEMPLATES)
        self._ensure_active_user(context)
        self._ensure_payload_organization(payload.organization_id, context)
        previous = self._get_template(template_id, context.organization_id)
        previous["active"] = False
        template = self._build_template(
            payload,
            version=previous["version"] + 1,
            active=True,
        )
        self.templates[template["id"]] = template
        return template

    def archive_template(self, template_id: str, context: RequestContext) -> dict:
        assert_permission(context, Permission.MANAGE_TEMPLATES)
        self._ensure_active_user(context)
        template = self._get_template(template_id, context.organization_id)
        template["active"] = False
        return template

    def apply_template(
        self,
        case_id: str,
        payload: ApplyTemplateRequest,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_CLINICAL_CASES)
        self._ensure_active_user(context)
        self._get_case(case_id, context.organization_id)
        template = self._get_template(payload.template_id, context.organization_id)
        if not template["active"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template is archived.",
            )
        phases: list[dict] = []

        for index, template_phase in enumerate(template["phases"]):
            phase = {
                "id": self._new_id("case_phase"),
                "template_phase_id": template_phase["id"],
                "name": template_phase["name"],
                "order_index": template_phase["order_index"],
                "objective": template_phase["objective"],
                "minimum_days": template_phase["minimum_days"],
                "exit_summary": template_phase["exit_summary"],
                "status": (
                    PhaseStatus.CURRENT.value
                    if index == 0
                    else PhaseStatus.LOCKED.value
                ),
                "clinician_note": None,
                "milestones": [],
            }
            for template_milestone in template_phase["milestones"]:
                phase["milestones"].append(
                    {
                        "id": self._new_id("case_milestone"),
                        "template_milestone_id": template_milestone["id"],
                        "title": template_milestone["title"],
                        "kind": template_milestone["kind"],
                        "required": template_milestone["required"],
                        "instructions": template_milestone["instructions"],
                        "status": MilestoneResultStatus.NOT_STARTED.value,
                        "recorded_by": None,
                        "recorded_at": None,
                        "notes": None,
                        "evidence_json": {},
                    }
                )
            phases.append(phase)

        self.case_plans[case_id] = phases
        return {
            "injury_case_id": case_id,
            "template_id": template["id"],
            "phases": phases,
        }
