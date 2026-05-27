from pydantic import ValidationError

from return_play.models import (
    AthleteCreate,
    ClearanceDecisionCreate,
    InjuryCaseCreate,
    ReturnPlanTemplateCreate,
    SymptomLogCreate,
    UserRole,
)


def test_athlete_create_captures_roster_identity() -> None:
    athlete = AthleteCreate(
        organization_id="org_demo",
        name="Demo Athlete",
        date_of_birth="2008-04-20",
        sport="Soccer",
        position="Midfielder",
        guardian_contact="guardian@example.com",
    )

    assert athlete.organization_id == "org_demo"
    assert athlete.active is True


def test_injury_case_create_requires_human_owner() -> None:
    injury_case = InjuryCaseCreate(
        organization_id="org_demo",
        athlete_id="athlete_demo",
        title="Left ankle sprain",
        injury_category="sprain",
        body_region="ankle",
        side="left",
        date_of_injury="2026-05-20",
        clinician_owner_id="user_clinician",
        summary="Rolled ankle during match.",
    )

    assert injury_case.status == "active"
    assert injury_case.clinician_owner_id == "user_clinician"


def test_template_create_models_editable_workflow_scaffold() -> None:
    template = ReturnPlanTemplateCreate(
        organization_id="org_demo",
        name="Generic lower limb staged return",
        injury_category="lower_limb",
        description="Editable staged plan for demo use.",
        created_by="user_clinician",
    )

    assert template.version == 1
    assert template.active is True


def test_symptom_log_rejects_out_of_range_pain() -> None:
    try:
        SymptomLogCreate(
            injury_case_id="case_demo",
            athlete_id="athlete_demo",
            date="2026-05-26",
            pain=11,
            swelling="none",
            confidence=4,
        )
    except ValidationError as exc:
        assert "less than or equal to 10" in str(exc)
    else:
        raise AssertionError("Expected pain validation failure")


def test_clearance_decision_requires_named_human_decision() -> None:
    decision = ClearanceDecisionCreate(
        injury_case_id="case_demo",
        phase_id="phase_demo",
        decision="hold",
        decided_by="user_clinician",
        decided_by_role=UserRole.CLINICIAN,
        rationale="Pain increased after workload progression.",
        restrictions="No contact practice.",
    )

    assert decision.decision == "hold"
    assert decision.decided_by_role == UserRole.CLINICIAN
