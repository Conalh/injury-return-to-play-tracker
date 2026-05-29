"""End-to-end checks against a real Postgres database.

Skipped unless RETURN_PLAY_DATABASE_URL points at Postgres, so the default
SQLite-only test run is unaffected. The Postgres CI job applies the Alembic
migrations to a fresh database and then runs these, which is the only place the
suite exercises the production database engine and the migration-produced
schema together.

The demo seed records a clearance decision and a share token — exactly the
writes that the clearance-decision foreign-key bug broke. A successful seed here
is the regression guard the SQLite suite could not provide.
"""

import os

import pytest
from fastapi.testclient import TestClient

from helpers import DEFAULT_AUTH_HEADERS
from return_play.api import create_persistent_app

DATABASE_URL = os.environ.get("RETURN_PLAY_DATABASE_URL", "")

pytestmark = pytest.mark.skipif(
    not DATABASE_URL.startswith("postgresql"),
    reason="requires RETURN_PLAY_DATABASE_URL pointing at a Postgres database",
)


@pytest.fixture
def client() -> TestClient:
    # No create_all here on purpose: the schema must come from the applied
    # Alembic migrations so a wrong migration (e.g. a bad FK target) fails here.
    test_client = TestClient(create_persistent_app(DATABASE_URL))
    test_client.headers.update(DEFAULT_AUTH_HEADERS)
    return test_client


def test_demo_seed_persists_clearance_and_share_against_postgres(
    client: TestClient,
) -> None:
    seed_response = client.post("/api/demo/seed")
    assert seed_response.status_code == 201, seed_response.text
    seed = seed_response.json()
    assert seed["already_seeded"] is False

    case_response = client.get(f"/api/injury-cases/{seed['injury_case_id']}")
    assert case_response.status_code == 200
    case = case_response.json()
    # The seed records a "hold" decision on the first applied phase; a held phase
    # remains the current workflow step.
    assert case["current_phase"]["status"] == "held"
    assert case["clearance_decisions"][-1]["decision"] == "hold"

    share_response = client.get(f"/api/share/{seed['share_token']}")
    assert share_response.status_code == 200
    assert share_response.json()["athlete_name"] == seed["athlete_name"]
