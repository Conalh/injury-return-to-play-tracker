import json
import time

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy import select

from helpers import auth_headers
from return_play.api import create_app, create_persistent_app
from return_play.auth import RequestContext, create_auth_token
from return_play.db import AuthTokenRevocation, Base, create_engine_for_url, create_session_factory


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


def test_local_logout_revokes_current_bearer_token(monkeypatch) -> None:
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

    assert client.get("/api/me").status_code == 200
    logout_response = client.post("/api/auth/logout")
    revoked_response = client.get("/api/me")

    assert logout_response.status_code == 200
    assert logout_response.json() == {"status": "logged_out"}
    assert revoked_response.status_code == 401
    assert revoked_response.json()["detail"] == "Bearer token has been revoked."


def test_auth_tokens_include_unique_revocation_ids(monkeypatch) -> None:
    monkeypatch.setenv("RETURN_PLAY_AUTH_MODE", "token")
    monkeypatch.setenv("RETURN_PLAY_AUTH_SECRET", "test-secret")
    context = RequestContext(
        actor_id="clinician_demo",
        role="clinician",
        organization_id="org_demo",
    )

    first_token = create_auth_token(context, secret="test-secret")
    second_token = create_auth_token(context, secret="test-secret")
    client = TestClient(create_app())

    assert first_token != second_token

    client.headers.update({"Authorization": f"Bearer {first_token}"})
    assert client.post("/api/auth/logout").status_code == 200

    client.headers.update({"Authorization": f"Bearer {first_token}"})
    assert client.get("/api/me").status_code == 401

    client.headers.update({"Authorization": f"Bearer {second_token}"})
    assert client.get("/api/me").status_code == 200


def test_persistent_logout_revocation_survives_app_restart(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("RETURN_PLAY_AUTH_MODE", "token")
    monkeypatch.setenv("RETURN_PLAY_AUTH_SECRET", "test-secret")
    database_url = f"sqlite:///{tmp_path / 'auth-revocation.db'}"
    engine = create_engine_for_url(database_url)
    Base.metadata.create_all(engine)
    token = create_auth_token(
        RequestContext(
            actor_id="clinician_demo",
            role="clinician",
            organization_id="org_demo",
        ),
        secret="test-secret",
    )

    first_client = TestClient(create_persistent_app(database_url))
    first_client.headers.update({"Authorization": f"Bearer {token}"})
    assert first_client.get("/api/me").status_code == 200
    assert first_client.post("/api/auth/logout").status_code == 200
    session_factory = create_session_factory(database_url)
    with session_factory() as session:
        stored_revocations = session.execute(select(AuthTokenRevocation)).scalars().all()
    assert len(stored_revocations) == 1
    assert stored_revocations[0].actor_id == "clinician_demo"
    assert stored_revocations[0].organization_id == "org_demo"

    second_client = TestClient(create_persistent_app(database_url))
    second_client.headers.update({"Authorization": f"Bearer {token}"})
    response = second_client.get("/api/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Bearer token has been revoked."


def test_oidc_provider_validates_issuer_audience_and_claim_mapping(monkeypatch) -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private_key.public_key()))
    public_jwk["kid"] = "return-play-test-key"
    token = jwt.encode(
        {
            "iss": "https://identity.example.com/",
            "aud": "return-play-api",
            "sub": "oidc_clinician",
            "exp": int(time.time()) + 3600,
            "jti": "oidc-token-1",
            "return_play_role": "clinician",
            "return_play_organization_id": "org_oidc",
        },
        private_key,
        algorithm="RS256",
        headers={"kid": "return-play-test-key"},
    )
    monkeypatch.setenv("RETURN_PLAY_AUTH_MODE", "token")
    monkeypatch.setenv("RETURN_PLAY_AUTH_PROVIDER", "oidc")
    monkeypatch.setenv("RETURN_PLAY_OIDC_ISSUER", "https://identity.example.com/")
    monkeypatch.setenv("RETURN_PLAY_OIDC_AUDIENCE", "return-play-api")
    monkeypatch.setenv("RETURN_PLAY_OIDC_JWKS_JSON", json.dumps({"keys": [public_jwk]}))
    client = TestClient(create_app())
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get("/api/me")

    assert response.status_code == 200
    assert response.json() == {
        "actor_id": "oidc_clinician",
        "role": "clinician",
        "organization_id": "org_oidc",
    }


def test_oidc_provider_rejects_wrong_audience(monkeypatch) -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private_key.public_key()))
    public_jwk["kid"] = "return-play-test-key"
    token = jwt.encode(
        {
            "iss": "https://identity.example.com/",
            "aud": "other-api",
            "sub": "oidc_clinician",
            "exp": int(time.time()) + 3600,
            "jti": "oidc-token-2",
            "return_play_role": "clinician",
            "return_play_organization_id": "org_oidc",
        },
        private_key,
        algorithm="RS256",
        headers={"kid": "return-play-test-key"},
    )
    monkeypatch.setenv("RETURN_PLAY_AUTH_MODE", "token")
    monkeypatch.setenv("RETURN_PLAY_AUTH_PROVIDER", "oidc")
    monkeypatch.setenv("RETURN_PLAY_OIDC_ISSUER", "https://identity.example.com/")
    monkeypatch.setenv("RETURN_PLAY_OIDC_AUDIENCE", "return-play-api")
    monkeypatch.setenv("RETURN_PLAY_OIDC_JWKS_JSON", json.dumps({"keys": [public_jwk]}))
    client = TestClient(create_app())
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get("/api/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "OIDC bearer token is invalid."
