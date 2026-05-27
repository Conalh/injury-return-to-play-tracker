from fastapi.testclient import TestClient

from return_play.api import create_app


def test_health_endpoint_reports_service_status() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "service": "return-play-api",
        "status": "ok",
    }


def test_api_routes_are_registered_under_api_prefix() -> None:
    route_paths = {route.path for route in create_app().routes}

    assert "/api/athletes" in route_paths
    assert "/api/injury-cases" in route_paths
    assert "/api/templates" in route_paths
