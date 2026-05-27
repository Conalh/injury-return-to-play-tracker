# API Service

FastAPI service for roster, injury case, template, evidence, readiness,
clearance, sharing, and reporting workflows.

## Current Scope

Goal 2 establishes the backend skeleton:

- FastAPI app factory and health endpoint.
- Initial API route placeholders.
- Pydantic request contracts for core V1 entities.
- SQLAlchemy metadata for the initial data model.
- Alembic baseline migration.
- Contract tests for the app, schemas, metadata, and migration.

Repository CRUD, authentication, permissions, readiness logic, and reporting are
intentionally deferred to later goals.

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

