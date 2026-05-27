from fastapi.testclient import TestClient

from helpers import auth_headers
from return_play.api import create_app
from return_play.auth import RequestContext, create_auth_token


def test_token_mode_rejects_anonymous_and_trusted_header_requests(monkeypatch) -> None:
    monkeypatch.setenv("RETURN_PLAY_AUTH_MODE", "token")
    monkeypatch.setenv("RETURN_PLAY_AUTH_SECRET", "test-secret")
    client = TestClient(create_app())
    client.headers.update(auth_headers())

    response = client.get("/api/athletes")

    assert response.status_code == 401
    assert response.json()["detail"] == "Bearer token required."


def test_token_mode_current_user_and_clinical_access_come_from_bearer_token(
    monkeypatch,
) -> None:
    monkeypatch.setenv("RETURN_PLAY_AUTH_MODE", "token")
    monkeypatch.setenv("RETURN_PLAY_AUTH_SECRET", "test-secret")
    token = create_auth_token(
        RequestContext(
            actor_id="clinician_demo",
            role="clinician",
            organization_id="org_demo",
        ),
        secret="test-secret",
    )
    client = TestClient(create_app())
    client.headers.update({"Authorization": f"Bearer {token}"})

    me_response = client.get("/api/me")
    athletes_response = client.get("/api/athletes", params={"organization_id": "org_demo"})

    assert me_response.status_code == 200
    assert me_response.json() == {
        "actor_id": "clinician_demo",
        "role": "clinician",
        "organization_id": "org_demo",
    }
    assert athletes_response.status_code == 200
    assert athletes_response.json() == {"items": []}


def test_token_mode_rejects_forged_organization_context(monkeypatch) -> None:
    monkeypatch.setenv("RETURN_PLAY_AUTH_MODE", "token")
    monkeypatch.setenv("RETURN_PLAY_AUTH_SECRET", "test-secret")
    token = create_auth_token(
        RequestContext(
            actor_id="clinician_demo",
            role="clinician",
            organization_id="org_demo",
        ),
        secret="test-secret",
    )
    client = TestClient(create_app())
    client.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "x-organization-id": "org_other",
        }
    )

    response = client.get("/api/athletes", params={"organization_id": "org_other"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Requested organization does not match request context."


def test_local_login_issues_token_and_logout_accepts_authenticated_session(
    monkeypatch,
) -> None:
    monkeypatch.setenv("RETURN_PLAY_AUTH_MODE", "token")
    monkeypatch.setenv("RETURN_PLAY_AUTH_SECRET", "test-secret")
    monkeypatch.setenv("RETURN_PLAY_LOCAL_AUTH_ENABLED", "1")
    monkeypatch.setenv("RETURN_PLAY_LOCAL_AUTH_EMAIL", "clinician@example.com")
    monkeypatch.setenv("RETURN_PLAY_LOCAL_AUTH_PASSWORD", "correct-password")
    monkeypatch.setenv("RETURN_PLAY_LOCAL_AUTH_ACTOR_ID", "clinician_demo")
    monkeypatch.setenv("RETURN_PLAY_LOCAL_AUTH_ROLE", "clinician")
    monkeypatch.setenv("RETURN_PLAY_LOCAL_AUTH_ORGANIZATION_ID", "org_demo")
    client = TestClient(create_app())

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "clinician@example.com",
            "password": "correct-password",
        },
    )
    assert login_response.status_code == 200
    assert login_response.json()["token_type"] == "bearer"
    token = login_response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    logout_response = client.post("/api/auth/logout")

    assert logout_response.status_code == 200
    assert logout_response.json() == {"status": "logged_out"}
