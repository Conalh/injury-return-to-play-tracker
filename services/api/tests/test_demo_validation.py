from helpers import create_client


def test_demo_seed_proves_complete_return_to_play_workflow() -> None:
    client = create_client()

    seed_response = client.post("/api/demo/seed")

    assert seed_response.status_code == 201
    seed = seed_response.json()
    case_id = seed["injury_case_id"]
    share_token = seed["share_token"]
    assert seed["athlete_name"] == "Riley Chen"
    assert seed["current_phase"] == "Restore motion"
    assert seed["can_auto_clear"] is False

    roster_response = client.get("/api/athletes", params={"organization_id": "org_demo"})
    assert roster_response.status_code == 200
    assert [athlete["name"] for athlete in roster_response.json()["items"]] == [
        "Riley Chen"
    ]

    case_response = client.get(f"/api/injury-cases/{case_id}")
    assert case_response.status_code == 200
    case_detail = case_response.json()
    assert case_detail["current_phase"]["name"] == "Restore motion"
    assert len(case_detail["symptom_logs"]) == 3
    assert len(case_detail["functional_tests"]) == 2
    assert len(case_detail["workload_sessions"]) == 2
    assert case_detail["clearance_decisions"][0]["decision"] == "hold"

    readiness_response = client.get(f"/api/injury-cases/{case_id}/readiness")
    assert readiness_response.status_code == 200
    readiness = readiness_response.json()
    assert readiness["can_auto_clear"] is False
    assert {
        "missing_required_milestones",
        "symptom_worsening",
        "workload_tolerance",
    }.issubset({signal["type"] for signal in readiness["signals"]})

    share_response = client.get(f"/api/share/{share_token}")
    assert share_response.status_code == 200
    share = share_response.json()
    assert share["athlete_name"] == "Riley Chen"
    assert share["participation_status"] == "Modified participation"
    assert "symptom_logs" not in share
    assert "guardian_contact" not in share

    report_response = client.get(f"/api/injury-cases/{case_id}/report")
    assert report_response.status_code == 200
    assert report_response.content.startswith(b"%PDF")

    audit_response = client.get(f"/api/injury-cases/{case_id}/audit-log")
    assert audit_response.status_code == 200
    event_types = [event["event_type"] for event in audit_response.json()["items"]]
    assert event_types[-3:] == [
        "clearance_decision_recorded",
        "share_created",
        "report_generated",
    ]
    assert {
        "milestone_evidence_recorded",
        "symptom_logged",
        "functional_test_logged",
        "workload_session_logged",
    }.issubset(event_types)


def test_demo_seed_is_idempotent_for_local_validation() -> None:
    client = create_client()

    first_seed = client.post("/api/demo/seed")
    second_seed = client.post("/api/demo/seed")

    assert first_seed.status_code == 201
    assert second_seed.status_code == 200
    assert second_seed.json()["injury_case_id"] == first_seed.json()["injury_case_id"]

    roster_response = client.get("/api/athletes", params={"organization_id": "org_demo"})
    assert [athlete["name"] for athlete in roster_response.json()["items"]] == [
        "Riley Chen"
    ]
