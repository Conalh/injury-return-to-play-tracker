from fastapi.testclient import TestClient

from return_play.api import create_app


def test_clinician_can_create_case_apply_template_and_update_current_gate() -> None:
    client = TestClient(create_app())

    athlete_response = client.post(
        "/api/athletes",
        json={
            "organization_id": "org_demo",
            "name": "Demo Athlete",
            "date_of_birth": "2008-04-20",
            "sport": "Soccer",
            "position": "Midfielder",
            "guardian_contact": "guardian@example.com",
        },
    )
    assert athlete_response.status_code == 201
    athlete = athlete_response.json()

    roster_response = client.get("/api/athletes", params={"organization_id": "org_demo"})
    assert roster_response.status_code == 200
    assert [row["id"] for row in roster_response.json()["items"]] == [athlete["id"]]

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
                },
                {
                    "name": "Controlled practice",
                    "order_index": 1,
                    "objective": "Resume non-contact practice.",
                    "minimum_days": 3,
                    "exit_summary": "Practice workload tolerated.",
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
    template = template_response.json()

    apply_response = client.post(
        f"/api/injury-cases/{injury_case['id']}/apply-template",
        json={"template_id": template["id"]},
    )
    assert apply_response.status_code == 200
    applied = apply_response.json()
    assert [phase["status"] for phase in applied["phases"]] == ["current", "locked"]
    first_milestone = applied["phases"][0]["milestones"][0]
    assert first_milestone["status"] == "not_started"

    milestone_response = client.patch(
        f"/api/injury-cases/{injury_case['id']}/milestones/{first_milestone['id']}",
        json={
            "status": "passed",
            "recorded_by": "clinician_demo",
            "notes": "Symptoms reviewed with athlete.",
            "evidence_json": {"source": "clinician_review"},
        },
    )
    assert milestone_response.status_code == 200
    assert milestone_response.json()["status"] == "passed"

    note_response = client.post(
        f"/api/injury-cases/{injury_case['id']}/notes",
        json={
            "author_id": "clinician_demo",
            "body": "Hold contact drills until next review.",
        },
    )
    assert note_response.status_code == 201

    detail_response = client.get(f"/api/injury-cases/{injury_case['id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["current_phase"]["name"] == "Restore motion"
    assert detail["current_phase"]["milestones"][0]["status"] == "passed"
    assert detail["notes"][0]["body"] == "Hold contact drills until next review."


def test_roster_is_filtered_by_organization() -> None:
    client = TestClient(create_app())

    for organization_id in ["org_a", "org_b"]:
        response = client.post(
            "/api/athletes",
            json={
                "organization_id": organization_id,
                "name": f"Athlete {organization_id}",
                "date_of_birth": "2008-04-20",
                "sport": "Soccer",
            },
        )
        assert response.status_code == 201

    response = client.get("/api/athletes", params={"organization_id": "org_a"})

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["organization_id"] == "org_a"
