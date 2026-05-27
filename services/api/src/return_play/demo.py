from __future__ import annotations

from return_play.auth import RequestContext
from return_play.models import (
    ApplyTemplateRequest,
    AthleteCreate,
    ClearanceDecisionCreate,
    ClinicianNoteCreate,
    FunctionalTestCreate,
    InjuryCaseCreate,
    MilestoneResultUpdate,
    ReturnPlanTemplateWithPhasesCreate,
    ShareTokenCreate,
    SymptomLogCreate,
    WorkloadSessionCreate,
)


def seed_demo_workflow(repository, context: RequestContext) -> dict:
    existing_demo = _find_demo_case(repository, context)
    if existing_demo is not None:
        return _demo_seed_response(
            repository,
            existing_demo,
            context,
            already_seeded=True,
        )

    athlete = repository.create_athlete(
        AthleteCreate(
            organization_id=context.organization_id,
            name="Riley Chen",
            date_of_birth="2008-04-20",
            sport="Soccer",
            position="Midfielder",
            guardian_contact="guardian@example.com",
        ),
        context,
    )
    injury_case = repository.create_injury_case(
        InjuryCaseCreate(
            organization_id=context.organization_id,
            athlete_id=athlete["id"],
            title="Left ankle sprain",
            injury_category="sprain",
            body_region="ankle",
            side="left",
            date_of_injury="2026-05-20",
            clinician_owner_id=context.actor_id,
            summary="Rolled ankle during match. Monitoring symptoms and workload.",
        ),
        context,
    )
    template = repository.create_template(
        ReturnPlanTemplateWithPhasesCreate(
            organization_id=context.organization_id,
            name="Demo ankle return",
            injury_category="ankle",
            description="Seeded staged ankle return plan.",
            created_by=context.actor_id,
            phases=[
                {
                    "name": "Restore motion",
                    "order_index": 0,
                    "objective": "Move without symptom increase and complete review.",
                    "minimum_days": 2,
                    "exit_summary": "Motion and symptoms reviewed.",
                    "milestones": [
                        {
                            "title": "Pain remains below configured threshold",
                            "kind": "symptom",
                            "required": True,
                            "instructions": "Review symptom logs.",
                        },
                        {
                            "title": "Clinician reviews ankle motion",
                            "kind": "clinician_review",
                            "required": True,
                            "instructions": "Document range-of-motion review.",
                        },
                    ],
                },
                {
                    "name": "Controlled practice",
                    "order_index": 1,
                    "objective": "Resume non-contact practice with stable response.",
                    "minimum_days": 3,
                    "exit_summary": "Practice workload tolerated.",
                    "milestones": [
                        {
                            "title": "Complete controlled practice",
                            "kind": "workload",
                            "required": True,
                        }
                    ],
                },
            ],
        ),
        context,
    )
    applied = repository.apply_template(
        injury_case["id"],
        ApplyTemplateRequest(template_id=template["id"]),
        context,
    )
    clinician_review = applied["phases"][0]["milestones"][1]
    repository.update_milestone(
        injury_case["id"],
        clinician_review["id"],
        MilestoneResultUpdate(
            status="passed",
            recorded_by=context.actor_id,
            notes="Motion reviewed with athlete.",
            evidence_json={"source": "demo_seed"},
        ),
        context,
    )

    for date, pain, confidence in [
        ("2026-05-24", 2, 4),
        ("2026-05-25", 3, 4),
        ("2026-05-26", 5, 3),
    ]:
        repository.create_symptom_log(
            injury_case["id"],
            SymptomLogCreate(
                injury_case_id=injury_case["id"],
                athlete_id=athlete["id"],
                date=date,
                pain=pain,
                swelling="none",
                confidence=confidence,
            ),
            context,
        )

    for name, result_value, unit, passed in [
        ("Single leg hop", 92, "% symmetry", True),
        ("Ankle dorsiflexion", 5, "degree difference", True),
    ]:
        repository.create_functional_test(
            injury_case["id"],
            FunctionalTestCreate(
                injury_case_id=injury_case["id"],
                name=name,
                test_date="2026-05-26",
                result_value=result_value,
                unit=unit,
                passed=passed,
                recorded_by=context.actor_id,
            ),
            context,
        )

    for activity, completed, response in [
        ("Non-contact practice", True, "No symptom increase during session."),
        ("Change-of-direction ladder", False, "Symptom increase after session."),
    ]:
        repository.create_workload_session(
            injury_case["id"],
            WorkloadSessionCreate(
                injury_case_id=injury_case["id"],
                date="2026-05-26",
                activity=activity,
                duration_minutes=30 if completed else 12,
                intensity=5 if completed else 6,
                symptom_response=response,
                completed=completed,
            ),
            context,
        )

    repository.create_note(
        injury_case["id"],
        ClinicianNoteCreate(
            author_id=context.actor_id,
            body="Hold contact drills until next review.",
        ),
        context,
    )
    repository.create_clearance_decision(
        injury_case["id"],
        ClearanceDecisionCreate(
            injury_case_id=injury_case["id"],
            phase_id=applied["phases"][0]["id"],
            decision="hold",
            decided_by=context.actor_id,
            decided_by_role=context.role.value,
            rationale="Symptoms require clinician review before progression.",
            restrictions="No contact drills. No full-speed cutting.",
        ),
        context,
    )
    share = repository.create_share(
        injury_case["id"],
        ShareTokenCreate(
            injury_case_id=injury_case["id"],
            audience="coach",
            expires_in_days=7,
            created_by=context.actor_id,
            allowed_activities="Non-contact practice and assigned rehab work.",
            restricted_activities="No contact drills. No full-speed cutting.",
            clinician_note="Next review after symptom check.",
            next_review_date="2026-05-30",
        ),
        context,
    )
    readiness = repository.get_readiness(injury_case["id"], context)

    return {
        "athlete_id": athlete["id"],
        "athlete_name": athlete["name"],
        "injury_case_id": injury_case["id"],
        "current_phase": applied["phases"][0]["name"],
        "share_token": share["token"],
        "can_auto_clear": readiness["can_auto_clear"],
        "readiness_signal_count": len(readiness["signals"]),
        "already_seeded": False,
    }


def _find_demo_case(repository, context: RequestContext) -> dict | None:
    for injury_case in repository.injury_cases.values():
        if (
            injury_case["organization_id"] == context.organization_id
            and injury_case["title"] == "Left ankle sprain"
            and repository.athletes[injury_case["athlete_id"]]["name"] == "Riley Chen"
        ):
            return injury_case
    return None


def _demo_seed_response(
    repository,
    injury_case: dict,
    context: RequestContext,
    *,
    already_seeded: bool,
) -> dict:
    athlete = repository.athletes[injury_case["athlete_id"]]
    phases = repository.case_plans.get(injury_case["id"], [])
    current_phase = next(
        (phase for phase in phases if phase["status"] == "current"),
        None,
    )
    share = next(
        (
            share_token
            for share_token in repository.share_tokens.values()
            if share_token["injury_case_id"] == injury_case["id"]
            and share_token["audience"] == "coach"
            and share_token["revoked_at"] is None
        ),
        None,
    )
    readiness = repository.get_readiness(injury_case["id"], context)

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
