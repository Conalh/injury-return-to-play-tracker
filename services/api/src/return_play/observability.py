from __future__ import annotations

import json
import logging
import time
import uuid
from collections import Counter
from collections.abc import Callable
from contextvars import ContextVar
from dataclasses import dataclass, field

from fastapi import FastAPI, Request
from starlette.responses import Response

from return_play.config import get_settings


REQUEST_ID_HEADER = "x-request-id"
request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)
request_logger = logging.getLogger("return_play.requests")
error_tracking_logger = logging.getLogger("return_play.error_tracking")


@dataclass
class ObservabilityState:
    started_at: float = field(default_factory=time.time)
    requests_total: int = 0
    errors_total: int = 0
    responses_by_status: Counter[str] = field(default_factory=Counter)
    requests_by_method: Counter[str] = field(default_factory=Counter)

    def record(self, *, method: str, status_code: int) -> None:
        self.requests_total += 1
        self.responses_by_status[str(status_code)] += 1
        self.requests_by_method[method] += 1
        if status_code >= 500:
            self.errors_total += 1

    def snapshot(self) -> dict:
        return {
            "service": get_settings().service_name,
            "uptime_seconds": max(0, int(time.time() - self.started_at)),
            "requests_total": self.requests_total,
            "errors_total": self.errors_total,
            "responses_by_status": dict(sorted(self.responses_by_status.items())),
            "requests_by_method": dict(sorted(self.requests_by_method.items())),
        }


def configure_observability(app: FastAPI) -> ObservabilityState:
    state = ObservabilityState()
    app.state.observability = state

    @app.middleware("http")
    async def observability_middleware(
        request: Request,
        call_next: Callable,
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        token = request_id_context.set(request_id)
        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as exc:
            capture_exception(exc, request_id=request_id, path=request.url.path)
            raise
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            state.record(method=request.method, status_code=status_code)
            request_logger.info(
                json.dumps(
                    {
                        "event": "http_request",
                        "method": request.method,
                        "path": request.url.path,
                        "request_id": request_id,
                        "status_code": status_code,
                        "duration_ms": duration_ms,
                    },
                    sort_keys=True,
                )
            )
            request_id_context.reset(token)
            if "response" in locals():
                response.headers[REQUEST_ID_HEADER] = request_id

    return state


def current_request_id() -> str | None:
    return request_id_context.get()


def capture_exception(exc: Exception, *, request_id: str, path: str) -> None:
    settings = get_settings()
    if not settings.error_tracking_dsn:
        return
    error_tracking_logger.error(
        json.dumps(
            {
                "event": "error_captured",
                "error_type": type(exc).__name__,
                "path": path,
                "request_id": request_id,
            },
            sort_keys=True,
        )
    )
