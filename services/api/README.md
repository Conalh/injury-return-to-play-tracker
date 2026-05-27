# API Service

FastAPI service for roster, injury case, template, evidence, readiness,
clearance, sharing, and reporting workflows.

## Current Scope

Goal 2 established the backend skeleton:

- FastAPI app factory and health endpoint.
- Pydantic request contracts for core V1 entities.
- SQLAlchemy metadata for the initial data model.
- Alembic baseline migration.
- Contract tests for the app, schemas, metadata, and migration.

Goal 3 adds the first clinician workflow behavior:

- Create and list athletes.
- Create injury cases.
- Create and list staged return-plan templates.
- Apply a template to an injury case.
- Read case detail with current phase, milestone statuses, and clinician notes.
- Update milestone status with evidence metadata.
- Add clinician notes.

The runtime repository is currently in-memory. SQLAlchemy metadata and Alembic
migrations are kept aligned with the workflow concepts, but request handlers do
not yet persist to Postgres. Authentication, permissions, readiness logic, and
reporting are intentionally deferred to later goals.

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .[dev]
```

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Migration Commands

```powershell
.\.venv\Scripts\alembic.exe heads
.\.venv\Scripts\alembic.exe upgrade head
```

The default `alembic.ini` URL points to local Postgres:

```text
postgresql://postgres:postgres@localhost:5432/return_play
```
