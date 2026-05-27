from fastapi.testclient import TestClient

from helpers import create_client


def test_share_token_exposes_limited_view_and_audit_events() -> None:
    client = create_client()
    injury_case = _create_case(client)

    share_response = client.post(
        f"/api/injury-cases/{injury_case['id']}/share",
        json={
            "injury_case_id": injury_case["id"],
            "audience": "coach",
            "expires_in_days": 7,
            "created_by": "clinician_demo",
            "allowed_activities": "Non-contact practice and rehab work.",
            "restricted_activities": "No contact drills. No full-speed cutting.",
            "clinician_note": "Next review after symptom check.",
        },
    )

    assert share_response.status_code == 201
    share = share_response.json()
    assert share["token"]
    assert share["audience"] == "coach"
    assert share["token_hash"] != share["token"]
    assert share["revoked_at"] is None

    limited_response = client.get(f"/api/share/{share['token']}")

    assert limited_response.status_code == 200
    limited = limited_response.json()
    assert limited == {
        "audience": "coach",
        "athlete_name": "Demo Athlete",
        "sport": "Soccer",
        "injury_title": "Left ankle sprain",
        "current_phase": None,
        "participation_status": "Modified participation",
        "allowed_activities": "Non-contact practice and rehab work.",
        "restricted_activities": "No contact drills. No full-speed cutting.",
        "next_review_date": None,
        "clearance_status": (
            "Awaiting named clinician decision. "
            "This shared view is not medical clearance."
        ),
        "clinician_note": "Next review after symptom check.",
    }
    assert "guardian_contact" not in limited
    assert "date_of_birth" not in limited
    assert "symptom_logs" not in limited
    assert "notes" not in limited

    audit_response = client.get(f"/api/injury-cases/{injury_case['id']}/audit-log")

    assert audit_response.status_code == 200
    assert audit_response.json()["items"][0]["event_type"] == "share_created"


def test_share_token_can_be_revoked() -> None:
    client = create_client()
    injury_case = _create_case(client)
    share = _create_share(client, injury_case["id"])

    revoke_response = client.post(
        f"/api/share/{share['token']}/revoke",
        json={"revoked_by": "clinician_demo"},
    )

    assert revoke_response.status_code == 200
    assert revoke_response.json()["revoked_at"] is not None
    assert client.get(f"/api/share/{share['token']}").status_code == 410

    audit_response = client.get(f"/api/injury-cases/{injury_case['id']}/audit-log")
    assert [event["event_type"] for event in audit_response.json()["items"]] == [
        "share_created",
        "share_revoked",
    ]


def test_pdf_report_endpoint_returns_pdf_and_records_audit_event() -> None:
    client = create_client()
    injury_case = _create_case(client)

    response = client.get(f"/api/injury-cases/{injury_case['id']}/report")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
    assert b"Return-to-Play Status Report" in response.content

    audit_response = client.get(f"/api/injury-cases/{injury_case['id']}/audit-log")
    assert audit_response.json()["items"][0]["event_type"] == "report_generated"


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


def _create_share(client: TestClient, case_id: str) -> dict:
    share_response = client.post(
        f"/api/injury-cases/{case_id}/share",
        json={
            "injury_case_id": case_id,
            "audience": "guardian",
            "expires_in_days": 7,
            "created_by": "clinician_demo",
            "allowed_activities": "Rehab work only.",
            "restricted_activities": "No practice.",
            "clinician_note": "Review next week.",
        },
    )
    assert share_response.status_code == 201
    return share_response.json()
