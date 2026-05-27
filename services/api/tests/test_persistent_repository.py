from pathlib import Path

from fastapi.testclient import TestClient

from helpers import DEFAULT_AUTH_HEADERS
from return_play.api import create_persistent_app, create_runtime_app
from return_play.db import Base, create_engine_for_url


def test_persistent_repository_survives_app_restart(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'return_play.db'}"
    engine = create_engine_for_url(database_url)
    Base.metadata.create_all(engine)

    first_client = TestClient(create_persistent_app(database_url))
    first_client.headers.update(DEFAULT_AUTH_HEADERS)

    seed_response = first_client.post("/api/demo/seed")

    assert seed_response.status_code == 201
    seed = seed_response.json()
    case_id = seed["injury_case_id"]
    share_token = seed["share_token"]

    second_client = TestClient(create_persistent_app(database_url))
    second_client.headers.update(DEFAULT_AUTH_HEADERS)

    roster_response = second_client.get(
        "/api/athletes",
        params={"organization_id": "org_demo"},
    )
    case_response = second_client.get(f"/api/injury-cases/{case_id}")
    share_response = second_client.get(f"/api/share/{share_token}")

    assert roster_response.status_code == 200
    assert [athlete["name"] for athlete in roster_response.json()["items"]] == [
        "Riley Chen"
    ]
    assert case_response.status_code == 200
    assert case_response.json()["current_phase"]["name"] == "Restore motion"
    assert len(case_response.json()["symptom_logs"]) == 3
    assert len(case_response.json()["workload_sessions"]) == 2
    assert share_response.status_code == 200
    assert share_response.json()["athlete_name"] == "Riley Chen"


def test_runtime_app_uses_persistent_repository_when_database_url_is_configured(
    tmp_path: Path,
    monkeypatch,
) -> None:
    database_url = f"sqlite:///{tmp_path / 'runtime.db'}"
    engine = create_engine_for_url(database_url)
    Base.metadata.create_all(engine)
    monkeypatch.setenv("RETURN_PLAY_DATABASE_URL", database_url)

    first_client = TestClient(create_runtime_app())
    first_client.headers.update(DEFAULT_AUTH_HEADERS)
    seed = first_client.post("/api/demo/seed").json()

    second_client = TestClient(create_runtime_app())
    second_client.headers.update(DEFAULT_AUTH_HEADERS)
    response = second_client.get(f"/api/injury-cases/{seed['injury_case_id']}")

    assert response.status_code == 200
    assert response.json()["current_phase"]["name"] == "Restore motion"
