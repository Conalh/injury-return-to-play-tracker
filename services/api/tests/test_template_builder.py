from helpers import create_client


def template_payload(name: str = "Shoulder staged return") -> dict:
    return {
        "organization_id": "org_demo",
        "name": name,
        "injury_category": "shoulder",
        "description": "Two-stage shoulder plan.",
        "created_by": "clinician_demo",
        "phases": [
            {
                "name": "Restore range",
                "order_index": 0,
                "objective": "Pain-free range of motion.",
                "minimum_days": 2,
                "exit_summary": "Range reviewed.",
                "milestones": [
                    {
                        "title": "Full pain-free range",
                        "kind": "range_of_motion",
                        "required": True,
                        "instructions": "Compare to baseline.",
                    }
                ],
            }
        ],
    }


def test_template_can_be_read_versioned_archived_and_blocked_from_apply() -> None:
    client = create_client()

    create_response = client.post("/api/templates", json=template_payload())
    assert create_response.status_code == 201
    original = create_response.json()

    detail_response = client.get(f"/api/templates/{original['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["phases"][0]["milestones"][0]["title"] == "Full pain-free range"

    update_payload = template_payload("Shoulder staged return revised")
    update_payload["phases"].append(
        {
            "name": "Controlled strength",
            "order_index": 1,
            "objective": "Build load tolerance.",
            "minimum_days": 3,
            "exit_summary": "Strength reviewed.",
            "milestones": [
                {
                    "title": "Complete resisted external rotation",
                    "kind": "strength",
                    "required": True,
                }
            ],
        }
    )
    update_response = client.patch(f"/api/templates/{original['id']}", json=update_payload)

    assert update_response.status_code == 200
    revised = update_response.json()
    assert revised["id"] != original["id"]
    assert revised["version"] == 2
    assert revised["active"] is True
    assert [phase["name"] for phase in revised["phases"]] == [
        "Restore range",
        "Controlled strength",
    ]

    old_detail = client.get(f"/api/templates/{original['id']}")
    assert old_detail.status_code == 200
    assert old_detail.json()["active"] is False

    archive_response = client.post(f"/api/templates/{revised['id']}/archive")
    assert archive_response.status_code == 200
    assert archive_response.json()["active"] is False

    athlete = client.post(
        "/api/athletes",
        json={
            "organization_id": "org_demo",
            "name": "Template Apply Athlete",
            "date_of_birth": "2009-01-15",
            "sport": "Volleyball",
        },
    ).json()
    injury_case = client.post(
        "/api/injury-cases",
        json={
            "organization_id": "org_demo",
            "athlete_id": athlete["id"],
            "title": "Right shoulder strain",
            "injury_category": "strain",
            "body_region": "shoulder",
            "side": "right",
            "date_of_injury": "2026-05-22",
            "clinician_owner_id": "clinician_demo",
        },
    ).json()

    apply_response = client.post(
        f"/api/injury-cases/{injury_case['id']}/apply-template",
        json={"template_id": revised["id"]},
    )
    assert apply_response.status_code == 400
    assert apply_response.json()["detail"] == "Template is archived."
