from return_play.auth import RequestContext
from return_play.models import UserRole
from return_play.repositories import InMemoryWorkflowRepository

from helpers import create_client


def test_sensitive_report_and_share_reads_are_audited_and_filterable() -> None:
    client = create_client()
    seed_response = client.post("/api/demo/seed")
    assert seed_response.status_code == 201
    seed = seed_response.json()

    share_response = client.get(f"/api/share/{seed['share_token']}")
    assert share_response.status_code == 200

    report_response = client.get(f"/api/injury-cases/{seed['injury_case_id']}/report")
    assert report_response.status_code == 200

    audit_response = client.get(f"/api/injury-cases/{seed['injury_case_id']}/audit-log")
    assert audit_response.status_code == 200
    event_types = [event["event_type"] for event in audit_response.json()["items"]]
    assert "share_view_read" in event_types
    assert "sensitive_export_read" in event_types

    share_read_response = client.get(
        f"/api/injury-cases/{seed['injury_case_id']}/audit-log?event_type=share_view_read",
    )
    assert share_read_response.status_code == 200
    share_read_events = share_read_response.json()["items"]
    assert share_read_events
    assert {event["event_type"] for event in share_read_events} == {"share_view_read"}

    actor_response = client.get(
        f"/api/injury-cases/{seed['injury_case_id']}/audit-log?actor_id=clinician_demo",
    )
    assert actor_response.status_code == 200
    actor_events = actor_response.json()["items"]
    assert actor_events
    assert {event["actor_id"] for event in actor_events} == {"clinician_demo"}
    assert "sensitive_export_read" in {event["event_type"] for event in actor_events}


def test_in_memory_audit_log_returns_immutable_record_copies() -> None:
    repository = InMemoryWorkflowRepository()
    context = RequestContext(
        actor_id="clinician_demo",
        role=UserRole.CLINICIAN,
        organization_id="org_demo",
    )
    seed = repository.seed_demo(context)

    audit_log = repository.get_audit_log(seed["injury_case_id"], context)
    share_created = next(
        event for event in audit_log["items"] if event["event_type"] == "share_created"
    )
    share_created["event_type"] = "tampered"
    share_created["metadata_json"]["audience"] = "tampered"

    fresh_audit_log = repository.get_audit_log(seed["injury_case_id"], context)
    fresh_share_created = next(
        event for event in fresh_audit_log["items"] if event["event_type"] == "share_created"
    )
    assert fresh_share_created["metadata_json"]["audience"] == "coach"
