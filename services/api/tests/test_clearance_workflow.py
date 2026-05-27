from fastapi.testclient import TestClient

from helpers import create_client


def test_phase_advances_only_after_named_human_decision() -> None:
    client = create_client()
    injury_case = _create_case_with_two_phase_plan(client)
    first_phase, second_phase = injury_case["phases"]
    milestone = first_phase["milestones"][0]

    milestone_response = client.patch(
        f"/api/injury-cases/{injury_case['id']}/milestones/{milestone['id']}",
        json={
            "status": "passed",
            "recorded_by": "clinician_demo",
            "notes": "Gate evidence reviewed.",
            "evidence_json": {"source": "clearance_workflow_test"},
        },
    )
    assert milestone_response.status_code == 200

    pre_decision_phases = client.get(f"/api/injury-cases/{injury_case['id']}/phases")
    assert pre_decision_phases.status_code == 200
    assert [phase["status"] for phase in pre_decision_phases.json()["items"]] == [
        "current",
        "locked",
    ]

    advance_response = client.post(
        f"/api/injury-cases/{injury_case['id']}/clearance",
        json={
            "injury_case_id": injury_case["id"],
            "phase_id": first_phase["id"],
            "decision": "advance",
            "decided_by": "clinician_demo",
            "decided_by_role": "clinician",
            "rationale": "Required evidence reviewed by clinician.",
            "restrictions": "Non-contact practice only.",
        },
    )
    assert advance_response.status_code == 201

    post_decision_phases = client.get(f"/api/injury-cases/{injury_case['id']}/phases")
    assert post_decision_phases.status_code == 200
    assert [phase["status"] for phase in post_decision_phases.json()["items"]] == [
        "passed",
        "current",
    ]

    detail_response = client.get(f"/api/injury-cases/{injury_case['id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["current_phase"]["id"] == second_phase["id"]
    assert detail["clearance_decisions"][-1]["decided_by"] == "clinician_demo"
    assert detail["clearance_decisions"][-1]["rationale"] == (
        "Required evidence reviewed by clinician."
    )

    audit_response = client.get(f"/api/injury-cases/{injury_case['id']}/audit-log")
    assert audit_response.status_code == 200
    event = audit_response.json()["items"][-1]
    assert event["event_type"] == "clearance_decision_recorded"
    assert event["metadata_json"] == {
        "decision": "advance",
        "decided_by_role": "clinician",
        "phase_id": first_phase["id"],
    }


def test_full_clearance_decision_marks_case_cleared() -> None:
    client = create_client()
    injury_case = _create_case_with_two_phase_plan(client)
    current_phase = injury_case["phases"][0]

    response = client.post(
        f"/api/injury-cases/{injury_case['id']}/clearance",
        json={
            "injury_case_id": injury_case["id"],
            "phase_id": current_phase["id"],
            "decision": "clear_full",
            "decided_by": "clinician_demo",
            "decided_by_role": "clinician",
            "rationale": "Athlete cleared after clinician review.",
            "restrictions": "Full unrestricted participation.",
        },
    )

    assert response.status_code == 201
    detail_response = client.get(f"/api/injury-cases/{injury_case['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["status"] == "cleared"


def test_hold_decision_keeps_held_phase_visible_as_current_workflow_step() -> None:
    client = create_client()
    injury_case = _create_case_with_two_phase_plan(client)
    current_phase = injury_case["phases"][0]

    response = client.post(
        f"/api/injury-cases/{injury_case['id']}/clearance",
        json={
            "injury_case_id": injury_case["id"],
            "phase_id": current_phase["id"],
            "decision": "hold",
            "decided_by": "clinician_demo",
            "decided_by_role": "clinician",
            "rationale": "Symptoms require review before progression.",
            "restrictions": "No contact drills.",
        },
    )

    assert response.status_code == 201
    detail_response = client.get(f"/api/injury-cases/{injury_case['id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["current_phase"]["id"] == current_phase["id"]
    assert detail["current_phase"]["status"] == "held"

    readiness_response = client.get(f"/api/injury-cases/{injury_case['id']}/readiness")
    assert readiness_response.status_code == 200
    assert readiness_response.json()["current_phase_id"] == current_phase["id"]


def _create_case_with_two_phase_plan(client: TestClient) -> dict:
    athlete_response = client.post(
        "/api/athletes",
        json={
            "organization_id": "org_demo",
            "name": "Clearance Athlete",
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
        },
    )
    assert case_response.status_code == 201
    injury_case = case_response.json()

    template_response = client.post(
        "/api/templates",
        json={
            "organization_id": "org_demo",
            "name": "Clearance plan",
            "injury_category": "ankle",
            "created_by": "clinician_demo",
            "phases": [
                {
                    "name": "Restore motion",
                    "order_index": 0,
                    "minimum_days": 1,
                    "milestones": [
                        {
                            "title": "Pain-free walk",
                            "kind": "function",
                            "required": True,
                        }
                    ],
                },
                {
                    "name": "Controlled practice",
                    "order_index": 1,
                    "minimum_days": 2,
                    "milestones": [
                        {
                            "title": "Complete controlled practice",
                            "kind": "workload",
                            "required": True,
                        }
                    ],
                },
            ],
        },
    )
    assert template_response.status_code == 201

    apply_response = client.post(
        f"/api/injury-cases/{injury_case['id']}/apply-template",
        json={"template_id": template_response.json()["id"]},
    )
    assert apply_response.status_code == 200
    return {**injury_case, "phases": apply_response.json()["phases"]}
