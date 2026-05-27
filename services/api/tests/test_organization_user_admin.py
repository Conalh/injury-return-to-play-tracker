from pathlib import Path

from fastapi.testclient import TestClient

from helpers import auth_headers
from return_play.api import create_persistent_app
from return_play.db import Base, create_engine_for_url


def test_admin_can_setup_organization_invite_user_change_role_and_deactivate(
    tmp_path: Path,
) -> None:
    client = _persistent_admin_client(tmp_path)

    organization_response = client.post(
        "/api/admin/organization",
        json={"name": "Goal 14 Sports Medicine", "timezone": "America/Los_Angeles"},
    )
    organization = organization_response.json()

    invite_response = client.post(
        "/api/admin/users/invitations",
        json={
            "organization_id": organization["id"],
            "email": "trainer@example.com",
            "name": "Taylor Trainer",
            "role": "clinician",
        },
    )
    invited_user = invite_response.json()

    role_response = client.patch(
        f"/api/admin/users/{invited_user['id']}/role",
        json={"role": "athletic_trainer"},
    )

    deactivate_response = client.post(
        f"/api/admin/users/{invited_user['id']}/deactivate",
        json={"deactivated_by": "admin_demo"},
    )

    audit_response = client.get(
        "/api/admin/audit-log",
        params={"organization_id": organization["id"]},
    )

    assert organization_response.status_code == 201
    assert organization == {
        "id": "org_goal14",
        "name": "Goal 14 Sports Medicine",
        "timezone": "America/Los_Angeles",
    }
    assert invite_response.status_code == 201
    assert invited_user["organization_id"] == "org_goal14"
    assert invited_user["email"] == "trainer@example.com"
    assert invited_user["role"] == "clinician"
    assert invited_user["active"] is True
    assert role_response.status_code == 200
    assert role_response.json()["role"] == "athletic_trainer"
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["active"] is False

    event_types = [event["event_type"] for event in audit_response.json()["items"]]
    assert event_types == [
        "organization_configured",
        "user_invited",
        "user_role_updated",
        "user_deactivated",
    ]


def test_admin_user_management_is_organization_bound(tmp_path: Path) -> None:
    client = _persistent_admin_client(tmp_path)

    response = client.post(
        "/api/admin/users/invitations",
        json={
            "organization_id": "org_other",
            "email": "trainer@example.com",
            "name": "Taylor Trainer",
            "role": "clinician",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Payload organization does not match request context."


def test_deactivated_user_loses_api_access(tmp_path: Path) -> None:
    admin = _persistent_admin_client(tmp_path)
    admin.post(
        "/api/admin/organization",
        json={"name": "Goal 14 Sports Medicine", "timezone": "America/Los_Angeles"},
    )
    invited_user = admin.post(
        "/api/admin/users/invitations",
        json={
            "organization_id": "org_goal14",
            "email": "trainer@example.com",
            "name": "Taylor Trainer",
            "role": "athletic_trainer",
        },
    ).json()
    admin.post(
        f"/api/admin/users/{invited_user['id']}/deactivate",
        json={"deactivated_by": "admin_demo"},
    )

    deactivated = TestClient(admin.app)
    deactivated.headers.update(
        auth_headers(
            actor_id=invited_user["id"],
            role="athletic_trainer",
            organization_id="org_goal14",
        )
    )

    response = deactivated.get("/api/athletes")

    assert response.status_code == 403
    assert response.json()["detail"] == "User is deactivated."


def _persistent_admin_client(tmp_path: Path) -> TestClient:
    database_url = f"sqlite:///{tmp_path / 'goal14.db'}"
    engine = create_engine_for_url(database_url)
    Base.metadata.create_all(engine)
    client = TestClient(create_persistent_app(database_url))
    client.headers.update(
        auth_headers(actor_id="admin_demo", role="admin", organization_id="org_goal14")
    )
    return client
