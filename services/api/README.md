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

Goal 4 adds evidence capture:

- Create and list symptom logs.
- Create and list functional test logs.
- Create and list workload sessions.
- Include evidence collections on injury case detail responses.
- Keep milestone evidence metadata on milestone status updates.

Goal 5 adds the readiness engine:

- `GET /api/injury-cases/{case_id}/readiness`.
- Missing required milestone signal.
- Symptom worsening signal.
- Workload tolerance signal.
- Clearance completeness signal.
- Source facts on every signal.
- Explicit `can_auto_clear: false` response field.

Goal 7 adds sharing, reports, and audit events:

- `POST /api/injury-cases/{case_id}/share`.
- `GET /api/share/{token}` for limited athlete, coach, or guardian status views.
- `POST /api/share/{token}/revoke`.
- `GET /api/injury-cases/{case_id}/report` for PDF status reports.
- `GET /api/injury-cases/{case_id}/audit-log`.
- Audit events for share creation, share revocation, and report generation.

Goal 8 adds privacy and permission hardening:

- Required local request context headers for protected `/api` routes:
  `x-actor-id`, `x-actor-role`, and `x-organization-id`.
- Role checks for clinician, athletic trainer, and admin workflows.
- Organization isolation for roster, template, case, evidence, readiness,
  report, share-management, and audit-log access.
- `POST /api/injury-cases/{case_id}/clearance` for named human clearance
  decisions.
- Audit events for clearance decisions.
- Non-diagnostic share language that states shared views are not medical
  clearance.

The runtime repository is currently in-memory. SQLAlchemy metadata and Alembic
migrations are kept aligned with the workflow concepts, but request handlers do
not yet persist to Postgres. The Goal 8 request context is a local development
contract for tests and future integration; production identity, sessions, and
token verification remain deferred.

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
