import json
import logging

from fastapi.testclient import TestClient

from return_play.api import create_app


def test_request_id_is_returned_and_structured_request_log_is_emitted(caplog) -> None:
    client = TestClient(create_app())

    with caplog.at_level(logging.INFO, logger="return_play.requests"):
        response = client.get("/health", headers={"x-request-id": "req-test-123"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-test-123"

    log_payloads = [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "return_play.requests"
    ]
    assert log_payloads
    assert log_payloads[-1]["event"] == "http_request"
    assert log_payloads[-1]["method"] == "GET"
    assert log_payloads[-1]["path"] == "/health"
    assert log_payloads[-1]["request_id"] == "req-test-123"
    assert log_payloads[-1]["status_code"] == 200
    assert "duration_ms" in log_payloads[-1]


def test_readiness_and_metrics_endpoints_report_runtime_state() -> None:
    client = TestClient(create_app())

    ready = client.get("/ready")
    client.get("/health")
    metrics = client.get("/metrics")

    assert ready.status_code == 200
    assert ready.json() == {
        "service": "return-play-api",
        "status": "ready",
    }
    assert metrics.status_code == 200
    body = metrics.json()
    assert body["service"] == "return-play-api"
    assert body["requests_total"] >= 2
    assert body["errors_total"] == 0
    assert body["responses_by_status"]["200"] >= 2
    assert body["requests_by_method"]["GET"] >= 2
    assert "uptime_seconds" in body


def test_error_tracking_seam_captures_exceptions_when_configured(monkeypatch, caplog) -> None:
    monkeypatch.setenv("RETURN_PLAY_ERROR_TRACKING_DSN", "local-test-dsn")
    app = create_app()

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("test failure")

    client = TestClient(app, raise_server_exceptions=False)

    with caplog.at_level(logging.ERROR, logger="return_play.error_tracking"):
        response = client.get("/boom", headers={"x-request-id": "req-error-123"})

    assert response.status_code == 500
    log_payloads = [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "return_play.error_tracking"
    ]
    assert log_payloads
    assert log_payloads[-1] == {
        "event": "error_captured",
        "error_type": "RuntimeError",
        "path": "/boom",
        "request_id": "req-error-123",
    }
