import json

from fastapi.testclient import TestClient

from helpers import create_client


def test_readiness_reports_missing_gates_and_never_auto_clears() -> None:
    client = create_client()
    injury_case, applied_plan = _create_case_with_plan(client)

    response = client.get(f"/api/injury-cases/{injury_case['id']}/readiness")

    assert response.status_code == 200
    readiness = response.json()
    signal_types = {signal["type"] for signal in readiness["signals"]}

    assert readiness["injury_case_id"] == injury_case["id"]
    assert readiness["can_auto_clear"] is False
    assert readiness["summary"]["missing_required_milestone_count"] == 1
    assert "missing_required_milestones" in signal_types
    assert "clearance_completeness" in signal_types
    assert readiness["signals"][0]["source_facts"]

    serialized = json.dumps(readiness).lower()
    assert "safe to play" not in serialized
    assert "clear athlete automatically" not in serialized

    missing_signal = _find_signal(readiness, "missing_required_milestones")
    assert missing_signal["source_facts"][0]["milestone_id"] == (
        applied_plan["phases"][0]["milestones"][0]["id"]
    )


def test_readiness_reports_symptom_and_workload_concerns_with_source_facts() -> None:
    client = create_client()
    injury_case, applied_plan = _create_case_with_plan(client)
    first_milestone = applied_plan["phases"][0]["milestones"][0]

    milestone_response = client.patch(
        f"/api/injury-cases/{injury_case['id']}/milestones/{first_milestone['id']}",
        json={
            "status": "passed",
            "recorded_by": "clinician_demo",
            "notes": "Reviewed current symptom and function evidence.",
            "evidence_json": {"source": "functional review"},
        },
    )
    assert milestone_response.status_code == 200

    for date, pain in [("2026-05-25", 2), ("2026-05-26", 5)]:
        response = client.post(
            f"/api/injury-cases/{injury_case['id']}/symptoms",
            json={
                "injury_case_id": injury_case["id"],
                "athlete_id": injury_case["athlete_id"],
                "date": date,
                "pain": pain,
                "swelling": "none",
                "confidence": 3,
            },
        )
        assert response.status_code == 201

    for date in ["2026-05-25", "2026-05-26"]:
        response = client.post(
            f"/api/injury-cases/{injury_case['id']}/workload-sessions",
            json={
                "injury_case_id": injury_case["id"],
                "date": date,
                "activity": "Controlled practice",
                "duration_minutes": 30,
                "intensity": 6,
                "symptom_response": "Symptom increase after session.",
                "completed": False,
            },
        )
        assert response.status_code == 201

    response = client.get(f"/api/injury-cases/{injury_case['id']}/readiness")

    assert response.status_code == 200
    readiness = response.json()
    signal_types = {signal["type"] for signal in readiness["signals"]}

    assert readiness["summary"]["missing_required_milestone_count"] == 0
    assert "symptom_worsening" in signal_types
    assert "workload_tolerance" in signal_types
    assert _find_signal(readiness, "symptom_worsening")["source_facts"][0]["pain"] == 5
    assert len(_find_signal(readiness, "workload_tolerance")["source_facts"]) == 2


def _create_case_with_plan(client: TestClient) -> tuple[dict, dict]:
    athlete_response = client.post(
        "/api/athletes",
        json={
            "organization_id": "org_demo",
            "name": "Demo Athlete",
            "date_of_birth": "2008-04-20",
            "sport": "Soccer",
        },
    )
    assert athlete_response.status_code == 201
    athlete = athlete_response.json()

    case_response = client.post(
        "/api/injury-cases",
        json={
            "organization_id": "org_demo",
            "athlete_id": athlete["id"],
            "title": "Left ankle sprain",
            "injury_category": "sprain",
            "body_region": "ankle",
            "side": "left",
            "date_of_injury": "2026-05-20",
            "clinician_owner_id": "clinician_demo",
            "summary": "Rolled ankle during match.",
        },
    )
    assert case_response.status_code == 201
    injury_case = case_response.json()

    template_response = client.post(
        "/api/templates",
        json={
            "organization_id": "org_demo",
            "name": "Generic ankle return",
            "injury_category": "ankle",
            "description": "Demo staged ankle plan.",
            "created_by": "clinician_demo",
            "phases": [
                {
                    "name": "Restore motion",
                    "order_index": 0,
                    "objective": "Move without symptom increase.",
                    "minimum_days": 2,
                    "exit_summary": "Motion and symptoms reviewed.",
                    "milestones": [
                        {
                            "title": "Pain remains below configured threshold",
                            "kind": "symptom",
                            "required": True,
                            "instructions": "Review symptom logs.",
                        }
                    ],
                }
            ],
        },
    )
    assert template_response.status_code == 201

    apply_response = client.post(
        f"/api/injury-cases/{injury_case['id']}/apply-template",
        json={"template_id": template_response.json()["id"]},
    )
    assert apply_response.status_code == 200
    return injury_case, apply_response.json()


def _find_signal(readiness: dict, signal_type: str) -> dict:
    return next(signal for signal in readiness["signals"] if signal["type"] == signal_type)
