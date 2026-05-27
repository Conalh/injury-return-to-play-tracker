# Local Production Compose

Status: Goal 28 local production packaging

This runbook starts the production-shaped local stack with Postgres, the FastAPI
API, and the Next.js web app. It is still a local development stack: identity is
kept in explicit `dev_headers` mode and secrets use local defaults.

## Services

- `db`: Postgres 16 with a named Docker volume.
- `api`: FastAPI image built from `services/api/Dockerfile`.
- `web`: Next.js image built from `apps/web/Dockerfile`.
- `seed-demo`: one-shot profile service that seeds the Riley Chen demo workflow
  through the API.

## Start

```powershell
docker compose up --build -d db api web
```

The API container runs `alembic upgrade head` before starting Uvicorn. Alembic
uses `RETURN_PLAY_DATABASE_URL`, so migrations target the compose Postgres
service instead of the local fallback URL in `alembic.ini`.

## Health Checks

```powershell
docker compose ps
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:3217
```

Open the web app at `http://127.0.0.1:3217`.

## Seed Demo Data

The web app runs in `api-demo` mode, so opening the dashboard seeds the demo
workflow automatically. To seed explicitly from compose:

```powershell
docker compose --profile seed run --rm seed-demo
```

## Stop

```powershell
docker compose down
```

To remove the local Postgres volume:

```powershell
docker compose down -v
```

## Local Ports

- Web: `http://127.0.0.1:3217`
- API: `http://127.0.0.1:8000`
- Postgres: `127.0.0.1:5432`
