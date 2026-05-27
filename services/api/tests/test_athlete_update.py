from helpers import create_client


def test_clinician_can_update_athlete_profile() -> None:
    client = create_client()
    athlete_response = client.post(
        "/api/athletes",
        json={
            "organization_id": "org_demo",
            "name": "Taylor Stone",
            "date_of_birth": "2008-04-20",
            "sport": "Soccer",
            "position": "Forward",
            "guardian_contact": "guardian@example.com",
        },
    )
    assert athlete_response.status_code == 201
    athlete = athlete_response.json()

    update_response = client.patch(
        f"/api/athletes/{athlete['id']}",
        json={
            "name": "Taylor Stone-Reed",
            "sport": "Basketball",
            "position": "Guard",
            "guardian_contact": "updated@example.com",
            "active": True,
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["name"] == "Taylor Stone-Reed"
    assert updated["sport"] == "Basketball"
    assert updated["position"] == "Guard"
    assert updated["guardian_contact"] == "updated@example.com"

    roster_response = client.get("/api/athletes", params={"organization_id": "org_demo"})
    assert roster_response.status_code == 200
    assert roster_response.json()["items"] == [updated]
