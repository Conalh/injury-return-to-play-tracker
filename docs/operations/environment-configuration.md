# Environment Configuration

Status: Goal 29 environment contract

The repository now has one checked-in example file, `.env.example`, and typed
runtime settings for both app surfaces. Do not commit real secrets in `.env` or
environment-specific files.

## Backend API

Backend settings are loaded through `return_play.config.ReturnPlaySettings`.
Local defaults keep demos and tests fast, while production startup validation
requires explicit safe values.

Required in production:

- `RETURN_PLAY_ENV=production`
- `RETURN_PLAY_DATABASE_URL`
- `RETURN_PLAY_AUTH_MODE=token`
- `RETURN_PLAY_AUTH_SECRET` with at least 32 characters
- `RETURN_PLAY_CORS_ORIGINS`

Forbidden in production:

- `RETURN_PLAY_AUTH_MODE=dev_headers`
- `RETURN_PLAY_LOCAL_AUTH_ENABLED=1`

Optional runtime controls:

- `RETURN_PLAY_MAX_REQUEST_BYTES`
- `RETURN_PLAY_AUTH_RATE_LIMIT_PER_MINUTE`
- `RETURN_PLAY_SHARE_RATE_LIMIT_PER_MINUTE`

## Frontend Web

Frontend settings are loaded through `apps/web/lib/env.ts`.

Local defaults:

- `RETURN_PLAY_ENV=local`
- `RETURN_PLAY_DATA_MODE=demo`
- `RETURN_PLAY_API_BASE_URL=http://127.0.0.1:8000`

Production validation:

- `RETURN_PLAY_DATA_MODE` must be `api` or `api-demo`.
- `RETURN_PLAY_API_BASE_URL` is required.

Use `RETURN_PLAY_API_TOKEN` for bearer-token mode. Without it, the frontend sends
the local development request-context headers configured by
`RETURN_PLAY_ACTOR_ID`, `RETURN_PLAY_ACTOR_ROLE`, and
`RETURN_PLAY_ORGANIZATION_ID`.

## Example File

Copy `.env.example` to a local `.env` when needed. `.env` files are ignored by
git; `.env.example` must stay placeholder-only.
