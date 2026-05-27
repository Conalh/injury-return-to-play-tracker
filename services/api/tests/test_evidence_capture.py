from fastapi.testclient import TestClient

from helpers import create_client


def test_clinician_can_capture_and_read_case_evidence() -> None:
    client = create_client()
    injury_case = _create_case(client)

    symptom_response = client.post(
        f"/api/injury-cases/{injury_case['id']}/symptoms",
        json={
            "injury_case_id": injury_case["id"],
            "athlete_id": injury_case["athlete_id"],
            "date": "2026-05-26",
            "pain": 3,
            "swelling": "mild",
            "confidence": 4,
            "notes": "Soreness after controlled practice.",
        },
    )
    assert symptom_response.status_code == 201
    symptom_log = symptom_response.json()
    assert symptom_log["pain"] == 3

    functional_response = client.post(
        f"/api/injury-cases/{injury_case['id']}/functional-tests",
        json={
            "injury_case_id": injury_case["id"],
            "name": "Single leg hop",
            "test_date": "2026-05-26",
            "result_value": 92,
            "unit": "percent",
            "side_to_side_difference_percent": 8,
            "passed": True,
            "recorded_by": "clinician_demo",
            "notes": "Good control on involved side.",
        },
    )
    assert functional_response.status_code == 201
    functional_test = functional_response.json()
    assert functional_test["passed"] is True

    workload_response = client.post(
        f"/api/injury-cases/{injury_case['id']}/workload-sessions",
        json={
            "injury_case_id": injury_case["id"],
            "date": "2026-05-26",
            "activity": "Non-contact practice",
            "duration_minutes": 30,
            "intensity": 5,
            "symptom_response": "No symptom increase during session.",
            "completed": True,
            "notes": "Stayed within planned workload.",
        },
    )
    assert workload_response.status_code == 201
    workload_session = workload_response.json()
    assert workload_session["completed"] is True

    symptoms = client.get(f"/api/injury-cases/{injury_case['id']}/symptoms")
    functional_tests = client.get(
        f"/api/injury-cases/{injury_case['id']}/functional-tests"
    )
    workload_sessions = client.get(
        f"/api/injury-cases/{injury_case['id']}/workload-sessions"
    )

    assert symptoms.status_code == 200
    assert symptoms.json()["items"] == [symptom_log]
    assert functional_tests.status_code == 200
    assert functional_tests.json()["items"] == [functional_test]
    assert workload_sessions.status_code == 200
    assert workload_sessions.json()["items"] == [workload_session]

    detail_response = client.get(f"/api/injury-cases/{injury_case['id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["symptom_logs"] == [symptom_log]
    assert detail["functional_tests"] == [functional_test]
    assert detail["workload_sessions"] == [workload_session]


def test_evidence_capture_rejects_mismatched_case_id() -> None:
    client = create_client()
    injury_case = _create_case(client)

    response = client.post(
        f"/api/injury-cases/{injury_case['id']}/symptoms",
        json={
            "injury_case_id": "case_other",
            "athlete_id": injury_case["athlete_id"],
            "date": "2026-05-26",
            "pain": 3,
            "swelling": "mild",
            "confidence": 4,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Evidence payload case does not match route."


def _create_case(client: TestClient) -> dict:
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
    return case_response.json()
