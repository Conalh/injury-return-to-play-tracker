from pathlib import Path

from fastapi.testclient import TestClient

from helpers import create_client
from return_play.api import create_app


def test_security_headers_are_added_to_api_responses() -> None:
    client = create_client()

    response = client.get("/health")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["content-security-policy"] == "default-src 'none'; frame-ancestors 'none'"


def test_cors_policy_allows_configured_origin_and_rejects_unknown_origin(monkeypatch) -> None:
    monkeypatch.setenv("RETURN_PLAY_CORS_ORIGINS", "http://localhost:3217,https://app.example.com")
    client = TestClient(create_app())

    allowed = client.options(
        "/api/me",
        headers={
            "Origin": "https://app.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    rejected = client.options(
        "/api/me",
        headers={
            "Origin": "https://unknown.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert allowed.status_code in {200, 204}
    assert allowed.headers["access-control-allow-origin"] == "https://app.example.com"
    assert "access-control-allow-origin" not in rejected.headers


def test_request_body_size_limit_rejects_oversized_payload(monkeypatch) -> None:
    monkeypatch.setenv("RETURN_PLAY_MAX_REQUEST_BYTES", "64")
    client = TestClient(create_app())

    response = client.post(
        "/api/auth/login",
        json={"email": "clinician@example.com", "password": "x" * 128},
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Request body is too large."


def test_auth_login_rate_limit_blocks_repeated_attempts(monkeypatch) -> None:
    monkeypatch.setenv("RETURN_PLAY_AUTH_RATE_LIMIT_PER_MINUTE", "2")
    monkeypatch.setenv("RETURN_PLAY_LOCAL_AUTH_ENABLED", "1")
    monkeypatch.setenv("RETURN_PLAY_LOCAL_AUTH_EMAIL", "clinician@example.com")
    monkeypatch.setenv("RETURN_PLAY_LOCAL_AUTH_PASSWORD", "correct-password")
    monkeypatch.setenv("RETURN_PLAY_LOCAL_AUTH_ACTOR_ID", "clinician_demo")
    monkeypatch.setenv("RETURN_PLAY_LOCAL_AUTH_ROLE", "clinician")
    monkeypatch.setenv("RETURN_PLAY_LOCAL_AUTH_ORGANIZATION_ID", "org_demo")
    client = TestClient(create_app())

    for _ in range(2):
        response = client.post(
            "/api/auth/login",
            json={"email": "clinician@example.com", "password": "wrong-password"},
        )
        assert response.status_code == 401

    blocked = client.post(
        "/api/auth/login",
        json={"email": "clinician@example.com", "password": "wrong-password"},
    )

    assert blocked.status_code == 429
    assert blocked.json()["detail"] == "Too many requests."


def test_share_link_rate_limit_blocks_repeated_reads(monkeypatch) -> None:
    monkeypatch.setenv("RETURN_PLAY_SHARE_RATE_LIMIT_PER_MINUTE", "2")
    client = create_client()
    seed = client.post("/api/demo/seed").json()

    for _ in range(2):
        response = client.get(f"/api/share/{seed['share_token']}")
        assert response.status_code == 200

    blocked = client.get(f"/api/share/{seed['share_token']}")

    assert blocked.status_code == 429
    assert blocked.json()["detail"] == "Too many requests."


def test_security_workflow_blocks_high_dependency_risk_and_scans_secrets() -> None:
    root = Path(__file__).parents[3]
    workflow = (root / ".github" / "workflows" / "security.yml").read_text()
    secret_scan = (root / "scripts" / "scan-secrets.ps1").read_text()

    assert "npm audit --audit-level=high" in workflow
    assert "pip-audit --strict --skip-editable" in workflow
    assert "scripts/scan-secrets.ps1" in workflow
    assert '"/scripts/scan-secrets.ps1"' in secret_scan
    assert '.FullName.Replace("\\", "/")' in secret_scan
    assert "BEGIN " + "PRIVATE KEY" in secret_scan
    assert "ghp" + "_" in secret_scan
