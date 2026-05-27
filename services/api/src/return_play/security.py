from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import Response

from return_play.config import get_settings


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}

DEFAULT_CORS_ORIGINS = (
    "http://127.0.0.1:3217",
    "http://127.0.0.1:3227",
    "http://localhost:3217",
    "http://localhost:3227",
)


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, *, limit: int, window_seconds: int = 60) -> bool:
        now = time.monotonic()
        hits = self._hits[key]
        while hits and now - hits[0] >= window_seconds:
            hits.popleft()
        if len(hits) >= limit:
            return False
        hits.append(now)
        return True


def configure_security(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "x-actor-id",
            "x-actor-role",
            "x-organization-id",
        ],
    )

    rate_limiter = InMemoryRateLimiter()

    @app.middleware("http")
    async def security_baseline_middleware(
        request: Request,
        call_next: Callable,
    ) -> Response:
        size_response = _reject_oversized_request(request)
        if size_response is not None:
            return _with_security_headers(size_response)

        rate_limit_response = _reject_rate_limited_request(request, rate_limiter)
        if rate_limit_response is not None:
            return _with_security_headers(rate_limit_response)

        response = await call_next(request)
        return _with_security_headers(response)


def _reject_oversized_request(request: Request) -> JSONResponse | None:
    max_bytes = get_settings().max_request_bytes
    content_length = request.headers.get("content-length")
    if content_length is None:
        return None
    try:
        request_size = int(content_length)
    except ValueError:
        return None
    if request_size <= max_bytes:
        return None
    return JSONResponse(
        {"detail": "Request body is too large."},
        status_code=413,
    )


def _reject_rate_limited_request(
    request: Request,
    rate_limiter: InMemoryRateLimiter,
) -> JSONResponse | None:
    path = request.url.path
    client_host = request.client.host if request.client else "unknown"
    if path == "/api/auth/login":
        limit = get_settings().auth_rate_limit_per_minute
        key = f"auth:{client_host}"
    elif path.startswith("/api/share/"):
        limit = get_settings().share_rate_limit_per_minute
        key = f"share:{client_host}:{path}"
    else:
        return None

    if rate_limiter.allow(key, limit=limit):
        return None
    return JSONResponse({"detail": "Too many requests."}, status_code=429)


def _with_security_headers(response: Response) -> Response:
    for name, value in SECURITY_HEADERS.items():
        response.headers.setdefault(name, value)
    return response


def _cors_origins() -> list[str]:
    configured = get_settings().cors_origin_list
    if configured:
        return configured
    return list(DEFAULT_CORS_ORIGINS)
