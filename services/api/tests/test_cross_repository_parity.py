"""Behavioral parity between the two workflow repository implementations.

The API can be backed by either InMemoryWorkflowRepository (demo/tests) or
SqlAlchemyWorkflowRepository (production Postgres, exercised here over SQLite).
These run identical request sequences against both backends and assert the same
observable outcomes, so behavioral divergence — like the clearance-decision FK
target bug that only surfaced against a real database — is caught here instead
of in production.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from helpers import DEFAULT_AUTH_HEADERS
from return_play.api import create_app, create_persistent_app
from return_play.db import Base, create_engine_for_url


def _in_memory_client(_tmp_path: Path) -> TestClient:
    client = TestClient(create_app())
    client.headers.update(DEFAULT_AUTH_HEADERS)
    return client


def _sqlalchemy_client(tmp_path: Path) -> TestClient:
    database_url = f"sqlite:///{tmp_path / 'parity.db'}"
    Base.metadata.create_all(create_engine_for_url(database_url))
    client = TestClient(create_persistent_app(database_url))
    client.headers.update(DEFAULT_AUTH_HEADERS)
    return client


_BACKENDS = {"in_memory": _in_memory_client, "sqlalchemy": _sqlalchemy_client}


@pytest.fixture(params=sorted(_BACKENDS))
def workflow_client(request: pytest.FixtureRequest, tmp_path: Path) -> TestClient:
    return _BACKENDS[request.param](tmp_path)


def _create_case_with_two_phase_plan(client: TestClient) -> dict:
    athlete = client.post(
        "/api/athletes",
        json={
            "organization_id": "org_demo",
            "name": "Parity Athlete",
            "date_of_birth": "2008-04-20",
            "sport": "Soccer",
        },
    ).json()

    injury_case = client.post(
        "/api/injury-cases",
        json={
            "organization_id": "org_demo",
            "athlete_id": athlete["id"],
            "title": "Left ankle sprain",
            "injury_category": "sprain",
            "body_region": "ankle",
            "side": "left",
            "date_of_injury": "2026-05-20",
            "clinician_owner_id": "clinician_demo",
        },
    ).json()

    template = client.post(
        "/api/templates",
        json={
            "organization_id": "org_demo",
            "name": "Clearance plan",
            "injury_category": "ankle",
            "created_by": "clinician_demo",
            "phases": [
                {
                    "name": "Restore motion",
                    "order_index": 0,
                    "minimum_days": 1,
                    "milestones": [
                        {"title": "Pain-free walk", "kind": "function", "required": True}
                    ],
                },
                {
                    "name": "Controlled practice",
                    "order_index": 1,
                    "minimum_days": 2,
                    "milestones": [
                        {
                            "title": "Complete controlled practice",
                            "kind": "workload",
                            "required": True,
                        }
                    ],
                },
            ],
        },
    ).json()

    apply_response = client.post(
        f"/api/injury-cases/{injury_case['id']}/apply-template",
        json={"template_id": template["id"]},
    )
    assert apply_response.status_code == 200
    return {**injury_case, "phases": apply_response.json()["phases"]}


def test_clearance_advance_behaves_identically_across_backends(
    workflow_client: TestClient,
) -> None:
    injury_case = _create_case_with_two_phase_plan(workflow_client)
    first_phase, second_phase = injury_case["phases"]
    milestone = first_phase["milestones"][0]

    milestone_response = workflow_client.patch(
        f"/api/injury-cases/{injury_case['id']}/milestones/{milestone['id']}",
        json={
            "status": "passed",
            "recorded_by": "clinician_demo",
            "notes": "Gate evidence reviewed.",
            "evidence_json": {"source": "cross_repository_parity"},
        },
    )
    assert milestone_response.status_code == 200

    # The clearance decision records against the case's applied phase id — the
    # exact write whose FK pointed at the wrong table. Both backends must accept
    # it and advance the workflow the same way.
    advance_response = workflow_client.post(
        f"/api/injury-cases/{injury_case['id']}/clearance",
        json={
            "injury_case_id": injury_case["id"],
            "phase_id": first_phase["id"],
            "decision": "advance",
            "decided_by": "clinician_demo",
            "decided_by_role": "clinician",
            "rationale": "Required evidence reviewed by clinician.",
            "restrictions": "Non-contact practice only.",
        },
    )
    assert advance_response.status_code == 201

    phases_response = workflow_client.get(f"/api/injury-cases/{injury_case['id']}/phases")
    assert phases_response.status_code == 200
    assert [phase["status"] for phase in phases_response.json()["items"]] == [
        "passed",
        "current",
    ]

    detail = workflow_client.get(f"/api/injury-cases/{injury_case['id']}").json()
    assert detail["current_phase"]["id"] == second_phase["id"]
    assert detail["clearance_decisions"][-1]["decided_by"] == "clinician_demo"
    assert detail["clearance_decisions"][-1]["rationale"] == (
        "Required evidence reviewed by clinician."
    )

    audit = workflow_client.get(f"/api/injury-cases/{injury_case['id']}/audit-log").json()
    assert audit["items"][-1]["event_type"] == "clearance_decision_recorded"
    assert audit["items"][-1]["metadata_json"] == {
        "decision": "advance",
        "decided_by_role": "clinician",
        "phase_id": first_phase["id"],
    }


def test_full_clearance_marks_case_cleared_across_backends(
    workflow_client: TestClient,
) -> None:
    injury_case = _create_case_with_two_phase_plan(workflow_client)
    current_phase = injury_case["phases"][0]

    response = workflow_client.post(
        f"/api/injury-cases/{injury_case['id']}/clearance",
        json={
            "injury_case_id": injury_case["id"],
            "phase_id": current_phase["id"],
            "decision": "clear_full",
            "decided_by": "clinician_demo",
            "decided_by_role": "clinician",
            "rationale": "Athlete cleared after clinician review.",
            "restrictions": "Full unrestricted participation.",
        },
    )
    assert response.status_code == 201

    detail = workflow_client.get(f"/api/injury-cases/{injury_case['id']}").json()
    assert detail["status"] == "cleared"
