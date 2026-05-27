from __future__ import annotations

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe
from uuid import uuid4

from fastapi import HTTPException, status

from return_play.auth import RequestContext
from return_play.demo import seed_demo_workflow
from return_play.models import (
    ApplyTemplateRequest,
    AthleteCreate,
    ClearanceDecisionCreate,
    ClinicianNoteCreate,
    FunctionalTestCreate,
    InjuryCaseCreate,
    MilestoneResultStatus,
    MilestoneResultUpdate,
    PhaseStatus,
    ReturnPlanTemplateWithPhasesCreate,
    ShareTokenCreate,
    ShareTokenRevoke,
    SymptomLogCreate,
    WorkloadSessionCreate,
)
from return_play.reports import build_case_report_pdf
from return_play.readiness import build_readiness


class InMemoryWorkflowRepository:
    def __init__(self) -> None:
        self.athletes: dict[str, dict] = {}
        self.injury_cases: dict[str, dict] = {}
        self.templates: dict[str, dict] = {}
        self.case_plans: dict[str, list[dict]] = {}
        self.notes: dict[str, list[dict]] = {}
        self.symptom_logs: dict[str, list[dict]] = {}
        self.functional_tests: dict[str, list[dict]] = {}
        self.workload_sessions: dict[str, list[dict]] = {}
        self.clearance_decisions: dict[str, list[dict]] = {}
        self.share_tokens: dict[str, dict] = {}
        self.audit_log_entries: dict[str, list[dict]] = {}

    def create_athlete(self, payload: AthleteCreate, context: RequestContext) -> dict:
        self._ensure_payload_organization(payload.organization_id, context)
        athlete = payload.model_dump(mode="json")
        athlete["id"] = self._new_id("athlete")
        self.athletes[athlete["id"]] = athlete
        return athlete

    def list_athletes(
        self,
        context: RequestContext,
        organization_id: str | None = None,
    ) -> dict[str, list[dict]]:
        self._ensure_requested_organization(organization_id, context)
        athletes = list(self.athletes.values())
        athletes = [
            athlete
            for athlete in athletes
            if athlete["organization_id"] == context.organization_id
        ]
        return {"items": athletes}

    def create_injury_case(self, payload: InjuryCaseCreate, context: RequestContext) -> dict:
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

    def get_injury_case_detail(self, case_id: str, context: RequestContext) -> dict:
        injury_case = self._get_case(case_id, context.organization_id)
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
            "symptom_logs": self.symptom_logs.get(case_id, []),
            "functional_tests": self.functional_tests.get(case_id, []),
            "workload_sessions": self.workload_sessions.get(case_id, []),
            "clearance_decisions": self.clearance_decisions.get(case_id, []),
        }

    def create_template(
        self,
        payload: ReturnPlanTemplateWithPhasesCreate,
        context: RequestContext,
    ) -> dict:
        self._ensure_payload_organization(payload.organization_id, context)
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

    def list_templates(
        self,
        context: RequestContext,
        organization_id: str | None = None,
    ) -> dict[str, list[dict]]:
        self._ensure_requested_organization(organization_id, context)
        templates = list(self.templates.values())
        templates = [
            template
            for template in templates
            if template["organization_id"] == context.organization_id
        ]
        return {"items": templates}

    def apply_template(
        self,
        case_id: str,
        payload: ApplyTemplateRequest,
        context: RequestContext,
    ) -> dict:
        self._get_case(case_id, context.organization_id)
        template = self._get_template(payload.template_id, context.organization_id)
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

    def list_case_phases(self, case_id: str, context: RequestContext) -> dict[str, list[dict]]:
        self._get_case(case_id, context.organization_id)
        return {"items": self.case_plans.get(case_id, [])}

    def update_milestone(
        self,
        case_id: str,
        milestone_id: str,
        payload: MilestoneResultUpdate,
        context: RequestContext,
    ) -> dict:
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
        self._get_case(case_id, context.organization_id)
        note = payload.model_dump(mode="json")
        note["id"] = self._new_id("note")
        note["injury_case_id"] = case_id
        note["created_at"] = self._now()
        self.notes.setdefault(case_id, []).append(note)
        return note

    def create_symptom_log(
        self,
        case_id: str,
        payload: SymptomLogCreate,
        context: RequestContext,
    ) -> dict:
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
        return symptom_log

    def list_symptom_logs(self, case_id: str, context: RequestContext) -> dict[str, list[dict]]:
        self._get_case(case_id, context.organization_id)
        return {"items": self.symptom_logs.get(case_id, [])}

    def create_functional_test(
        self,
        case_id: str,
        payload: FunctionalTestCreate,
        context: RequestContext,
    ) -> dict:
        self._validate_evidence_case(case_id, payload.injury_case_id, context)
        functional_test = payload.model_dump(mode="json")
        functional_test["id"] = self._new_id("functional_test")
        functional_test["recorded_at"] = self._now()
        self.functional_tests.setdefault(case_id, []).append(functional_test)
        return functional_test

    def list_functional_tests(
        self,
        case_id: str,
        context: RequestContext,
    ) -> dict[str, list[dict]]:
        self._get_case(case_id, context.organization_id)
        return {"items": self.functional_tests.get(case_id, [])}

    def create_workload_session(
        self,
        case_id: str,
        payload: WorkloadSessionCreate,
        context: RequestContext,
    ) -> dict:
        self._validate_evidence_case(case_id, payload.injury_case_id, context)
        workload_session = payload.model_dump(mode="json")
        workload_session["id"] = self._new_id("workload")
        workload_session["recorded_at"] = self._now()
        self.workload_sessions.setdefault(case_id, []).append(workload_session)
        return workload_session

    def list_workload_sessions(
        self,
        case_id: str,
        context: RequestContext,
    ) -> dict[str, list[dict]]:
        self._get_case(case_id, context.organization_id)
        return {"items": self.workload_sessions.get(case_id, [])}

    def get_readiness(self, case_id: str, context: RequestContext) -> dict:
        self._get_case(case_id, context.organization_id)
        phases = self.case_plans.get(case_id, [])
        current_phase = next(
            (phase for phase in phases if phase["status"] == PhaseStatus.CURRENT.value),
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
        self._validate_evidence_case(case_id, payload.injury_case_id, context)
        if payload.decided_by != context.actor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Clearance decision actor must match request context.",
            )

        decision = payload.model_dump(mode="json")
        decision["id"] = self._new_id("clearance")
        decision["decided_at"] = self._now()
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

    def create_share(
        self,
        case_id: str,
        payload: ShareTokenCreate,
        context: RequestContext,
    ) -> dict:
        self._validate_evidence_case(case_id, payload.injury_case_id, context)
        raw_token = token_urlsafe(24)
        token_hash = self._hash_token(raw_token)
        now = datetime.now(UTC)
        share = {
            **payload.model_dump(mode="json"),
            "id": self._new_id("share"),
            "token": raw_token,
            "token_hash": token_hash,
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(days=payload.expires_in_days)).isoformat(),
            "revoked_at": None,
        }
        self.share_tokens[token_hash] = share
        self._record_audit_event(
            case_id,
            "share_created",
            context.actor_id,
            {"audience": payload.audience.value, "share_id": share["id"]},
        )
        return share

    def get_share(self, token: str) -> dict:
        share = self._get_share_by_token(token)
        if share["revoked_at"] is not None:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Share token has been revoked.",
            )
        if datetime.fromisoformat(share["expires_at"]) <= datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Share token has expired.",
            )

        injury_case = self._get_case(share["injury_case_id"])
        athlete = self.athletes[injury_case["athlete_id"]]
        phases = self.case_plans.get(injury_case["id"], [])
        current_phase = next(
            (phase for phase in phases if phase["status"] == PhaseStatus.CURRENT.value),
            None,
        )
        return {
            "audience": share["audience"],
            "athlete_name": athlete["name"],
            "sport": athlete["sport"],
            "injury_title": injury_case["title"],
            "current_phase": current_phase["name"] if current_phase else None,
            "participation_status": "Modified participation",
            "allowed_activities": share["allowed_activities"],
            "restricted_activities": share["restricted_activities"],
            "next_review_date": share["next_review_date"],
            "clearance_status": (
                "Awaiting named clinician decision. "
                "This shared view is not medical clearance."
            ),
            "clinician_note": share["clinician_note"],
        }

    def revoke_share(
        self,
        token: str,
        payload: ShareTokenRevoke,
        context: RequestContext,
    ) -> dict:
        share = self._get_share_by_token(token)
        self._get_case(share["injury_case_id"], context.organization_id)
        if payload.revoked_by != context.actor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Revocation actor must match request context.",
            )
        if share["revoked_at"] is None:
            share["revoked_at"] = self._now()
            self._record_audit_event(
                share["injury_case_id"],
                "share_revoked",
                context.actor_id,
                {"audience": share["audience"], "share_id": share["id"]},
            )
        return share

    def build_report(self, case_id: str, context: RequestContext) -> bytes:
        injury_case = self._get_case(case_id, context.organization_id)
        athlete = self.athletes[injury_case["athlete_id"]]
        readiness = self.get_readiness(case_id, context)
        self._record_audit_event(
            case_id,
            "report_generated",
            context.actor_id,
            {"format": "pdf"},
        )
        return build_case_report_pdf(
            {
                **injury_case,
                "athlete_name": athlete["name"],
            },
            readiness,
        )

    def get_audit_log(self, case_id: str, context: RequestContext) -> dict[str, list[dict]]:
        self._get_case(case_id, context.organization_id)
        return {"items": self.audit_log_entries.get(case_id, [])}

    def seed_demo(self, context: RequestContext) -> dict:
        return seed_demo_workflow(self, context)

    def find_demo_case(self, context: RequestContext) -> dict | None:
        for injury_case in self.injury_cases.values():
            if (
                injury_case["organization_id"] == context.organization_id
                and injury_case["title"] == "Left ankle sprain"
                and self.athletes[injury_case["athlete_id"]]["name"] == "Riley Chen"
            ):
                return injury_case
        return None

    def demo_seed_response(
        self,
        injury_case: dict,
        context: RequestContext,
        *,
        already_seeded: bool,
    ) -> dict:
        athlete = self.athletes[injury_case["athlete_id"]]
        phases = self.case_plans.get(injury_case["id"], [])
        current_phase = next(
            (phase for phase in phases if phase["status"] == PhaseStatus.CURRENT.value),
            None,
        )
        share = next(
            (
                share_token
                for share_token in self.share_tokens.values()
                if share_token["injury_case_id"] == injury_case["id"]
                and share_token["audience"] == "coach"
                and share_token["revoked_at"] is None
            ),
            None,
        )
        readiness = self.get_readiness(injury_case["id"], context)

        return {
            "athlete_id": athlete["id"],
            "athlete_name": athlete["name"],
            "injury_case_id": injury_case["id"],
            "current_phase": current_phase["name"] if current_phase else None,
            "share_token": share["token"] if share else None,
            "can_auto_clear": readiness["can_auto_clear"],
            "readiness_signal_count": len(readiness["signals"]),
            "already_seeded": already_seeded,
        }

    def _get_case(self, case_id: str, organization_id: str | None = None) -> dict:
        try:
            injury_case = self.injury_cases[case_id]
        except KeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Injury case not found.",
            ) from exc
        if organization_id is not None and injury_case["organization_id"] != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Injury case not found.",
            )
        return injury_case

    def _get_template(self, template_id: str, organization_id: str | None = None) -> dict:
        try:
            template = self.templates[template_id]
        except KeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found.",
            ) from exc
        if organization_id is not None and template["organization_id"] != organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found.",
            )
        return template

    def _validate_evidence_case(
        self,
        route_case_id: str,
        payload_case_id: str,
        context: RequestContext,
    ) -> None:
        self._get_case(route_case_id, context.organization_id)
        if route_case_id != payload_case_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evidence payload case does not match route.",
            )

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

    def _get_share_by_token(self, token: str) -> dict:
        token_hash = self._hash_token(token)
        try:
            return self.share_tokens[token_hash]
        except KeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share token not found.",
            ) from exc

    def _record_audit_event(
        self,
        case_id: str,
        event_type: str,
        actor_id: str | None,
        metadata: dict,
    ) -> dict:
        event = {
            "id": self._new_id("audit"),
            "injury_case_id": case_id,
            "event_type": event_type,
            "actor_id": actor_id,
            "created_at": self._now(),
            "metadata_json": metadata,
        }
        self.audit_log_entries.setdefault(case_id, []).append(event)
        return event

    @staticmethod
    def _hash_token(token: str) -> str:
        return sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}_{uuid4().hex}"

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()
