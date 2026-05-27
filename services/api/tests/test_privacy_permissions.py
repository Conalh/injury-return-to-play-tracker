from fastapi.testclient import TestClient

from return_play.api import create_app

from helpers import auth_headers, create_client


def test_protected_routes_require_authenticated_request_context() -> None:
    client = TestClient(create_app())

    response = client.get("/api/athletes")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authenticated request context required."


def test_clinical_routes_reject_coach_role() -> None:
    client = TestClient(create_app())
    client.headers.update(auth_headers(role="coach"))

    response = client.post(
        "/api/athletes",
        json={
            "organization_id": "org_demo",
            "name": "Demo Athlete",
            "date_of_birth": "2008-04-20",
            "sport": "Soccer",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Role is not permitted for this action."


def test_organization_context_blocks_cross_tenant_case_access() -> None:
    client = create_client()
    injury_case = _create_case(client, "org_demo")

    client.headers.update(
        auth_headers(actor_id="clinician_other", organization_id="org_other")
    )

    response = client.get(f"/api/injury-cases/{injury_case['id']}")

    assert response.status_code == 404


def test_payload_organization_must_match_authenticated_context() -> None:
    client = create_client()

    response = client.post(
        "/api/athletes",
        json={
            "organization_id": "org_other",
            "name": "Demo Athlete",
            "date_of_birth": "2008-04-20",
            "sport": "Soccer",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Payload organization does not match request context."


def test_clearance_decision_is_named_and_audited() -> None:
    client = create_client()
    injury_case = _create_case(client, "org_demo")

    response = client.post(
        f"/api/injury-cases/{injury_case['id']}/clearance",
        json={
            "injury_case_id": injury_case["id"],
            "phase_id": "phase_demo",
            "decision": "hold",
            "decided_by": "clinician_demo",
            "decided_by_role": "clinician",
            "rationale": "Symptoms require clinician review before progression.",
            "restrictions": "No contact drills.",
        },
    )

    assert response.status_code == 201
    decision = response.json()
    assert decision["decided_by"] == "clinician_demo"
    assert decision["decided_at"]

    audit_response = client.get(f"/api/injury-cases/{injury_case['id']}/audit-log")
    event_types = [event["event_type"] for event in audit_response.json()["items"]]
    assert "clearance_decision_recorded" in event_types


def test_share_view_uses_non_diagnostic_clearance_language() -> None:
    client = create_client()
    injury_case = _create_case(client, "org_demo")
    share = _create_share(client, injury_case["id"])

    response = client.get(f"/api/share/{share['token']}")

    assert response.status_code == 200
    assert response.json()["clearance_status"] == (
        "Awaiting named clinician decision. This shared view is not medical clearance."
    )


def _create_case(client: TestClient, organization_id: str) -> dict:
    athlete_response = client.post(
        "/api/athletes",
        json={
            "organization_id": organization_id,
            "name": f"Athlete {organization_id}",
            "date_of_birth": "2008-04-20",
            "sport": "Soccer",
        },
    )
    assert athlete_response.status_code == 201
    athlete = athlete_response.json()

    case_response = client.post(
        "/api/injury-cases",
        json={
            "organization_id": organization_id,
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


def _create_share(client: TestClient, case_id: str) -> dict:
    share_response = client.post(
        f"/api/injury-cases/{case_id}/share",
        json={
            "injury_case_id": case_id,
            "audience": "coach",
            "expires_in_days": 7,
            "created_by": "clinician_demo",
            "allowed_activities": "Non-contact practice and rehab work.",
            "restricted_activities": "No contact drills. No full-speed cutting.",
            "clinician_note": "Next review after symptom check.",
        },
    )
    assert share_response.status_code == 201
    return share_response.json()
