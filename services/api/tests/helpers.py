from __future__ import annotations

from fastapi.testclient import TestClient

from return_play.api import create_app


DEFAULT_AUTH_HEADERS = {
    "x-actor-id": "clinician_demo",
    "x-actor-role": "clinician",
    "x-organization-id": "org_demo",
}


def auth_headers(
    *,
    actor_id: str = "clinician_demo",
    role: str = "clinician",
    organization_id: str = "org_demo",
) -> dict[str, str]:
    return {
        "x-actor-id": actor_id,
        "x-actor-role": role,
        "x-organization-id": organization_id,
    }


def create_client() -> TestClient:
    client = TestClient(create_app())
    client.headers.update(DEFAULT_AUTH_HEADERS)
    return client

