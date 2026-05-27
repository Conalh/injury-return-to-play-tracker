from fastapi.testclient import TestClient

from helpers import create_client


def test_evidence_entries_and_milestone_updates_are_audited() -> None:
    client = create_client()
    injury_case = _create_case_with_plan(client)
    milestone = injury_case["phases"][0]["milestones"][0]

    symptom = client.post(
        f"/api/injury-cases/{injury_case['id']}/symptoms",
        json={
            "injury_case_id": injury_case["id"],
            "athlete_id": injury_case["athlete_id"],
            "date": "2026-05-27",
            "pain": 8,
            "swelling": "moderate",
            "confidence": 2,
            "notes": "Symptoms increased after jogging.",
        },
    )
    assert symptom.status_code == 201

    functional = client.post(
        f"/api/injury-cases/{injury_case['id']}/functional-tests",
        json={
            "injury_case_id": injury_case["id"],
            "name": "Balance reach",
            "test_date": "2026-05-27",
            "result_value": 82,
            "unit": "percent",
            "side_to_side_difference_percent": 18,
            "passed": False,
            "recorded_by": "clinician_demo",
            "notes": "Loss of control late in test.",
        },
    )
    assert functional.status_code == 201

    workload = client.post(
        f"/api/injury-cases/{injury_case['id']}/workload-sessions",
        json={
            "injury_case_id": injury_case["id"],
            "date": "2026-05-27",
            "activity": "Jog intervals",
            "duration_minutes": 12,
            "intensity": 4,
            "symptom_response": "Pain increase during final interval.",
            "completed": False,
            "notes": "Stopped early.",
        },
    )
    assert workload.status_code == 201

    milestone_update = client.patch(
        f"/api/injury-cases/{injury_case['id']}/milestones/{milestone['id']}",
        json={
            "status": "failed",
            "recorded_by": "clinician_demo",
            "notes": "Evidence does not meet gate.",
            "evidence_json": {"source": "browser_evidence_form"},
        },
    )
    assert milestone_update.status_code == 200

    audit_response = client.get(f"/api/injury-cases/{injury_case['id']}/audit-log")
    assert audit_response.status_code == 200
    events = audit_response.json()["items"]
    event_types = [event["event_type"] for event in events]
    assert event_types == [
        "symptom_logged",
        "functional_test_logged",
        "workload_session_logged",
        "milestone_evidence_recorded",
    ]
    assert events[-1]["metadata_json"] == {
        "milestone_id": milestone["id"],
        "status": "failed",
    }


def _create_case_with_plan(client: TestClient) -> dict:
    athlete_response = client.post(
        "/api/athletes",
        json={
            "organization_id": "org_demo",
            "name": "Evidence Athlete",
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
            "name": "Evidence audit plan",
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
    return {**injury_case, "phases": apply_response.json()["phases"]}
