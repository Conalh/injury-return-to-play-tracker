# Observability

Status: Goal 30 observability contract

The API has a small built-in observability layer for local and production-path
runtime proof. It avoids logging clinical payloads or path parameters beyond the
request path already visible at the HTTP layer.

## Request IDs

Every response includes `x-request-id`.

- If the request includes `x-request-id`, the API preserves it.
- If it is missing, the API generates a UUID.
- Structured request logs include the same `request_id`.

## Structured Logs

The API emits one JSON log event per HTTP request through the
`return_play.requests` logger:

```json
{
  "event": "http_request",
  "method": "GET",
  "path": "/health",
  "request_id": "req-example",
  "status_code": 200,
  "duration_ms": 3.2
}
```

## Error Tracking Seam

Set `RETURN_PLAY_ERROR_TRACKING_DSN` to enable the current error-capture seam.
The implementation logs captured exception metadata through the
`return_play.error_tracking` logger. A hosted provider adapter can replace this
seam later without changing route code.

## System Endpoints

- `GET /health`: process liveness.
- `GET /ready`: application readiness.
- `GET /metrics`: low-cardinality JSON counters.

The metrics endpoint includes:

- `requests_total`
- `errors_total`
- `responses_by_status`
- `requests_by_method`
- `uptime_seconds`
