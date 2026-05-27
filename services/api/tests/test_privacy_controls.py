import pytest

from helpers import create_client
from return_play.privacy import BLOCKED_RESTRICTED_FIELDS, filter_share_view


def test_share_view_filter_contract_removes_blocked_fields() -> None:
    raw_view = {
        "audience": "coach",
        "athlete_name": "Demo Athlete",
        "sport": "Soccer",
        "injury_title": "Left ankle sprain",
        "current_phase": "Restore motion",
        "participation_status": "Modified participation",
        "allowed_activities": "Non-contact practice.",
        "restricted_activities": "No contact drills.",
        "next_review_date": None,
        "clearance_status": "Awaiting named clinician decision.",
        "clinician_note": "Review after symptoms.",
        "date_of_birth": "2008-04-20",
        "guardian_contact": "guardian@example.com",
        "symptom_logs": [{"pain": 4}],
        "functional_tests": [{"name": "Hop test"}],
        "workload_sessions": [{"activity": "Run"}],
        "clearance_decisions": [{"decision": "hold"}],
        "notes": [{"body": "Private clinician note"}],
        "token_hash": "hashed-token",
    }

    filtered = filter_share_view(raw_view, audience="coach")

    assert BLOCKED_RESTRICTED_FIELDS.isdisjoint(filtered)
    assert filtered["data_contract"]["audience"] == "coach"
    assert "date_of_birth" in filtered["data_contract"]["excluded_fields"]
    assert "symptom_logs" in filtered["data_contract"]["excluded_fields"]


def test_restricted_share_surfaces_never_receive_blocked_fields() -> None:
    client = create_client()
    seed_response = client.post("/api/demo/seed")
    assert seed_response.status_code == 201
    seed = seed_response.json()

    response = client.get(f"/api/share/{seed['share_token']}")

    assert response.status_code == 200
    body = response.json()
    assert BLOCKED_RESTRICTED_FIELDS.isdisjoint(body)
    assert body["data_contract"]["audience"] == "coach"
    assert "guardian_contact" in body["data_contract"]["excluded_fields"]


def test_privacy_data_controls_endpoint_exposes_retention_and_request_plan() -> None:
    client = create_client()

    response = client.get("/api/privacy/data-controls")

    assert response.status_code == 200
    controls = response.json()
    assert controls["retention_policy"]["case_records"]["hook"] == "case_retention_review"
    assert controls["retention_policy"]["audit_logs"]["default_action"] == "retain"
    assert "export_request" in controls["export_delete_request_plan"]
    assert "delete_request" in controls["export_delete_request_plan"]
    assert "minimum_necessary" in controls["phi_handling_checklist"]


@pytest.mark.parametrize("role", ["coach", "athlete", "guardian"])
def test_restricted_roles_cannot_read_clinical_detail_fields(role: str) -> None:
    clinical_client = create_client()
    seed_response = clinical_client.post("/api/demo/seed")
    assert seed_response.status_code == 201
    case_id = seed_response.json()["injury_case_id"]

    restricted_client = create_client()
    restricted_client.headers.update(
        {
            "x-actor-id": f"{role}_demo",
            "x-actor-role": role,
            "x-organization-id": "org_demo",
        }
    )

    response = restricted_client.get(f"/api/injury-cases/{case_id}")

    assert response.status_code == 403
