from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException, status

from return_play.models import (
    ApplyTemplateRequest,
    AthleteCreate,
    ClinicianNoteCreate,
    InjuryCaseCreate,
    MilestoneResultStatus,
    MilestoneResultUpdate,
    PhaseStatus,
    ReturnPlanTemplateWithPhasesCreate,
)


class InMemoryWorkflowRepository:
    def __init__(self) -> None:
        self.athletes: dict[str, dict] = {}
        self.injury_cases: dict[str, dict] = {}
        self.templates: dict[str, dict] = {}
        self.case_plans: dict[str, list[dict]] = {}
        self.notes: dict[str, list[dict]] = {}

    def create_athlete(self, payload: AthleteCreate) -> dict:
        athlete = payload.model_dump(mode="json")
        athlete["id"] = self._new_id("athlete")
        self.athletes[athlete["id"]] = athlete
        return athlete

    def list_athletes(self, organization_id: str | None = None) -> dict[str, list[dict]]:
        athletes = list(self.athletes.values())
        if organization_id is not None:
            athletes = [
                athlete
                for athlete in athletes
                if athlete["organization_id"] == organization_id
            ]
        return {"items": athletes}

    def create_injury_case(self, payload: InjuryCaseCreate) -> dict:
        if payload.athlete_id not in self.athletes:
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

    def get_injury_case_detail(self, case_id: str) -> dict:
        injury_case = self._get_case(case_id)
        phases = self.case_plans.get(case_id, [])
        current_phase = next(
            (phase for phase in phases if phase["status"] == PhaseStatus.CURRENT.value),
            None,
        )
        return {
            **injury_case,
            "phases": phases,
            "current_phase": current_phase,
            "notes": self.notes.get(case_id, []),
        }

    def create_template(self, payload: ReturnPlanTemplateWithPhasesCreate) -> dict:
        template = payload.model_dump(mode="json", exclude={"phases"})
        template["id"] = self._new_id("template")
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

        self.templates[template["id"]] = template
        return template

    def list_templates(self, organization_id: str | None = None) -> dict[str, list[dict]]:
        templates = list(self.templates.values())
        if organization_id is not None:
            templates = [
                template
                for template in templates
                if template["organization_id"] == organization_id
            ]
        return {"items": templates}

    def apply_template(self, case_id: str, payload: ApplyTemplateRequest) -> dict:
        self._get_case(case_id)
        template = self._get_template(payload.template_id)
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

    def list_case_phases(self, case_id: str) -> dict[str, list[dict]]:
        self._get_case(case_id)
        return {"items": self.case_plans.get(case_id, [])}

    def update_milestone(
        self,
        case_id: str,
        milestone_id: str,
        payload: MilestoneResultUpdate,
    ) -> dict:
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
                    return milestone

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found for injury case.",
        )

    def create_note(self, case_id: str, payload: ClinicianNoteCreate) -> dict:
        self._get_case(case_id)
        note = payload.model_dump(mode="json")
        note["id"] = self._new_id("note")
        note["injury_case_id"] = case_id
        note["created_at"] = self._now()
        self.notes.setdefault(case_id, []).append(note)
        return note

    def _get_case(self, case_id: str) -> dict:
        try:
            return self.injury_cases[case_id]
        except KeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Injury case not found.",
            ) from exc

    def _get_template(self, template_id: str) -> dict:
        try:
            return self.templates[template_id]
        except KeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found.",
            ) from exc

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}_{uuid4().hex}"

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()
