import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from helpers import auth_headers, create_client
from return_play.auth import RequestContext
from return_play.models import UserRole
from return_play.permissions import Permission, ROLE_PERMISSIONS, assert_permission
from return_play.repositories import InMemoryWorkflowRepository


CLINICAL_ROLES = {
    UserRole.ADMIN,
    UserRole.ATHLETIC_TRAINER,
    UserRole.CLINICIAN,
}

LIMITED_ROLES = {
    UserRole.ATHLETE,
    UserRole.COACH,
    UserRole.GUARDIAN,
}


def test_permission_matrix_grants_clinical_workflow_only_to_clinical_roles() -> None:
    for role in CLINICAL_ROLES:
        assert Permission.READ_CLINICAL_CASES in ROLE_PERMISSIONS[role]
        assert Permission.RECORD_CLEARANCE_DECISIONS in ROLE_PERMISSIONS[role]

    for role in LIMITED_ROLES:
        assert Permission.READ_SHARED_STATUS in ROLE_PERMISSIONS[role]
        assert Permission.READ_CLINICAL_CASES not in ROLE_PERMISSIONS[role]
        assert Permission.RECORD_CLEARANCE_DECISIONS not in ROLE_PERMISSIONS[role]


def test_service_permission_guard_rejects_limited_roles() -> None:
    context = RequestContext(
        actor_id="coach_demo",
        role=UserRole.COACH,
        organization_id="org_demo",
    )

    with pytest.raises(HTTPException) as exc_info:
        assert_permission(context, Permission.READ_CLINICAL_CASES)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Permission is not permitted for this action."


def test_repository_enforces_permissions_when_called_directly() -> None:
    repository = InMemoryWorkflowRepository()
    context = RequestContext(
        actor_id="coach_demo",
        role=UserRole.COACH,
        organization_id="org_demo",
    )

    with pytest.raises(HTTPException) as exc_info:
        repository.list_athletes(context)

    assert exc_info.value.status_code == 403


def test_route_permissions_reject_athlete_coach_and_guardian_roles() -> None:
    for role in ("athlete", "coach", "guardian"):
        client = TestClient(create_client().app)
        client.headers.update(auth_headers(actor_id=f"{role}_demo", role=role))

        response = client.get("/api/athletes")

        assert response.status_code == 403
        assert response.json()["detail"] == "Permission is not permitted for this action."


def test_admin_access_stays_organization_bound() -> None:
    client = create_client()
    athlete_response = client.post(
        "/api/athletes",
        json={
            "organization_id": "org_demo",
            "name": "Admin Boundary Athlete",
            "date_of_birth": "2008-04-20",
            "sport": "Soccer",
        },
    )
    assert athlete_response.status_code == 201

    admin = TestClient(client.app)
    admin.headers.update(
        auth_headers(actor_id="admin_other", role="admin", organization_id="org_other")
    )

    response = admin.get("/api/athletes", params={"organization_id": "org_demo"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Requested organization does not match request context."
