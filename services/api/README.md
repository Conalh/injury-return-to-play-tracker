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

Goal 9 adds demo seeding and complete workflow validation:

- `POST /api/demo/seed` creates the local Riley Chen demo workflow for the
  authenticated organization. First seed returns `201`; later calls return
  `200` with the existing seeded case.
- The seed covers athlete, injury case, staged return plan, milestone status,
  symptom logs, functional tests, workload sessions, clinician note, hold
  clearance decision, limited share link, readiness signals, PDF report, and
  audit log proof.
- The endpoint is intended for local/demo validation only and uses the
  in-memory repository.

Goal 10 adds the first persistent repository path:

- `RETURN_PLAY_DATABASE_URL` switches the runtime app from the in-memory
  repository to a SQLAlchemy-backed repository.
- The persistent repository supports the current workflow surface, including
  demo seed, roster, case detail, evidence, readiness, sharing, reports, and
  audit events.
- Runtime share and clearance columns are represented in SQLAlchemy metadata
  and Alembic migration `0004_goal_10`.
- In-memory remains the default when `RETURN_PLAY_DATABASE_URL` is not set, so
  local unit-style tests and demos can run without a database.

Goal 11 cleans up the repository boundary:

- Concrete repositories now live under `return_play.repositories`.
- Boundary modules define the athlete, case, template/plan, evidence,
  readiness, share/report/audit, and demo seed surfaces.
- Legacy imports from `return_play.repository` and
  `return_play.sql_repository` remain compatible.
- `tests/test_repository_boundaries.py` locks the package split without
  changing public API behavior.

Goal 12 adds the authentication foundation:

- `RETURN_PLAY_AUTH_MODE=dev_headers` keeps trusted local request headers for
  development and tests.
- `RETURN_PLAY_AUTH_MODE=token` disables trusted identity headers and requires
  an HMAC-signed bearer token.
- The provider decision is an OIDC-compatible bearer-token seam. The current
  HMAC token provider is local and replaceable; hosted OIDC validation can
  replace the verifier without changing route dependencies.
- `GET /api/me` returns the authenticated actor, role, and organization from
  the verified request context.
- `POST /api/auth/login` issues a bearer token only when the explicit local
  login provider is enabled with environment variables.
- `POST /api/auth/logout` provides the session boundary for clients; current
  tokens are stateless, so revocation remains future production-provider work.
- Token-mode tests prove anonymous requests are rejected, authenticated
  clinicians can access their organization, and forged organization headers do
  not override token identity.

The `dev_headers` mode is still a local development contract for tests and
manual API work. Production deployments should use token mode or a future OIDC
provider adapter, never trusted request headers.

Goal 13 formalizes authorization:

- `return_play.permissions` defines named permissions and the role matrix.
- API routes depend on `require_permission(...)` instead of broad clinical role
  lists.
- Concrete repositories call `assert_permission(...)` at public workflow entry
  points, so direct service calls cannot bypass route-level checks.
- Coaches, athletes, and guardians retain only shared-status permission until
  their portal surfaces exist.
- `docs/product/permission-matrix.md` is the human-readable matrix.

Goal 14 adds organization and user administration:

- `POST /api/admin/organization` configures the authenticated admin's
  organization.
- `POST /api/admin/users/invitations` creates an active invited user inside the
  admin's organization.
- `PATCH /api/admin/users/{user_id}/role` changes a user's role.
- `POST /api/admin/users/{user_id}/deactivate` deactivates a user.
- `GET /api/admin/audit-log` returns organization audit events for organization
  setup, invitations, role changes, and deactivation.
- Deactivated persisted users are rejected by protected repository-backed
  workflow access.
- Alembic migration `0005_goal_14` adds `users.active` and
  `organization_audit_log_entries`.

Goal 15 exposes the case list needed by the frontend API integration:

- `GET /api/injury-cases` returns organization-scoped injury cases for the
  authenticated clinical workflow user.
- The Next.js dashboard uses this endpoint with `/api/athletes`,
  `/api/injury-cases/{case_id}`, and readiness endpoints to render backend data.

Goal 16 adds athlete profile editing for the clinician creation UI:

- `PATCH /api/athletes/{athlete_id}` updates organization-scoped athlete
  profile fields behind the same manage-athlete permission as creation.
- The case creation UI continues to use `POST /api/athletes`,
  `POST /api/injury-cases`, `GET /api/templates`, and
  `POST /api/injury-cases/{case_id}/apply-template`.

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .[dev]
```

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Demo Seed

With the API running, seed the local demo workflow with the Goal 8 request
context headers:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/demo/seed `
  -Headers @{
    "x-actor-id" = "clinician_demo"
    "x-actor-role" = "clinician"
    "x-organization-id" = "org_demo"
  }
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

The API runtime uses this environment variable for the persistent repository:

```text
RETURN_PLAY_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/return_play
```

## Authentication Modes

Local header mode is the default:

```text
RETURN_PLAY_AUTH_MODE=dev_headers
```

Token mode requires a signing secret:

```text
RETURN_PLAY_AUTH_MODE=token
RETURN_PLAY_AUTH_SECRET=<long-random-secret>
```

The local login endpoint is disabled unless explicitly enabled:

```text
RETURN_PLAY_LOCAL_AUTH_ENABLED=1
RETURN_PLAY_LOCAL_AUTH_EMAIL=clinician@example.com
RETURN_PLAY_LOCAL_AUTH_PASSWORD=<local-password>
RETURN_PLAY_LOCAL_AUTH_ACTOR_ID=clinician_demo
RETURN_PLAY_LOCAL_AUTH_ROLE=clinician
RETURN_PLAY_LOCAL_AUTH_ORGANIZATION_ID=org_demo
```
