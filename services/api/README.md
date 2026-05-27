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

Goal 17 adds template builder support:

- `GET /api/templates/{template_id}` returns template detail with phases and
  milestones.
- `PATCH /api/templates/{template_id}` creates a new active version and
  archives the edited version.
- `POST /api/templates/{template_id}/archive` marks a template inactive.
- Archived templates cannot be applied to injury cases.

Goal 18 adds audit coverage for evidence entry:

- Symptom logs write `symptom_logged` audit events.
- Functional tests write `functional_test_logged` audit events.
- Workload sessions write `workload_session_logged` audit events.
- Milestone evidence updates write `milestone_evidence_recorded` audit events.

Goal 19 adds clearance workflow behavior:

- `POST /api/injury-cases/{case_id}/clearance` now applies named human
  decisions to case state.
- `hold` marks the selected case phase held.
- `advance` marks the current case phase passed and opens the next phase.
- `clear_full` marks the injury case cleared.
- `close_case` marks the injury case closed.
- Milestone evidence alone does not advance phases, and clearance decisions
  continue to write `clearance_decision_recorded` audit events.

Goal 20 uses the existing sharing API from the clinician UI:

- `POST /api/injury-cases/{case_id}/share` issues limited share tokens.
- `POST /api/share/{token}/revoke` revokes issued tokens.
- `GET /api/injury-cases/{case_id}/audit-log` supplies the case-detail share
  audit trail.
- Revoked tokens continue to return unavailable shared-view responses.

Goal 21 adds athlete symptom check-ins through limited share tokens:

- `POST /api/share/{token}/symptoms` accepts symptom check-ins for athlete
  audience share tokens.
- The endpoint derives injury case and athlete IDs from the token instead of
  accepting clinician-scoped identifiers from the browser.
- Coach and guardian shares cannot submit athlete symptoms.
- Accepted check-ins write `athlete_symptom_check_in` audit events and appear in
  clinician case detail symptom logs.

Goal 22 adds guardian acknowledgments through limited share tokens:

- `POST /api/share/{token}/guardian-acknowledgment` accepts acknowledgments for
  guardian audience share tokens.
- The endpoint derives the case from the token and rejects non-guardian shares.
- Accepted acknowledgments write `guardian_acknowledgment_recorded` audit
  events.

Goal 23 upgrades PDF reports:

- `GET /api/injury-cases/{case_id}/report` now includes status, phase,
  evidence, restrictions, clearance decisions, readiness signals, and audit
  metadata sections.
- Reports include a non-diagnostic disclaimer and avoid forbidden clearance
  language.
- PDF tests extract report text and verify stable renderable page dimensions
  with `pypdf`.

Goal 24 hardens audit logging:

- `return_play.audit` defines the shared audit event taxonomy.
- `GET /api/share/{token}` records `share_view_read` for successful limited
  share reads.
- `GET /api/injury-cases/{case_id}/report` records `sensitive_export_read` in
  addition to `report_generated`.
- `GET /api/injury-cases/{case_id}/audit-log` accepts `event_type`, `actor_id`,
  and bounded `limit` filters.
- In-memory audit-log reads return copied records so callers cannot mutate the
  stored audit trail.

Goal 25 adds privacy controls and data minimization:

- `return_play.privacy` defines the limited share-view allowlist and blocked
  restricted fields.
- `GET /api/share/{token}` filters through the shared privacy contract and
  includes a `data_contract` that names included and excluded fields.
- `GET /api/privacy/data-controls` returns retention policy hooks, the
  export/delete request plan, and the PHI handling checklist for protected
  clinical users.
- Tests prove restricted share surfaces do not receive blocked clinical fields
  and restricted roles remain blocked from clinical detail endpoints.

Goal 26 establishes the first security baseline:

- `return_play.security` configures secure response headers, CORS allowlisting,
  request body size limits, and per-process rate limits for `/api/auth/login`
  and `/api/share/*` routes.
- `RETURN_PLAY_CORS_ORIGINS`, `RETURN_PLAY_MAX_REQUEST_BYTES`,
  `RETURN_PLAY_AUTH_RATE_LIMIT_PER_MINUTE`, and
  `RETURN_PLAY_SHARE_RATE_LIMIT_PER_MINUTE` configure the runtime controls.
- `.github/workflows/security.yml` runs `npm audit --audit-level=high`,
  `pip-audit --strict`, and the repository secret scan.
- `scripts/scan-secrets.ps1` blocks common committed private key and token
  patterns.

Goal 27 adds the continuous integration contract:

- `.github/workflows/ci.yml` runs backend tests, Alembic migration head checks,
  the Next.js build, Playwright workflow tests, and dependency audits.
- `docs/operations/ci-required-checks.md` documents the branch-protection
  checks expected before merge.
- The security workflow remains responsible for the standalone secret scan
  status check.

Goal 28 adds local production packaging:

- `services/api/Dockerfile` builds the API runtime image.
- `compose.yml` runs Postgres, applies Alembic migrations, starts the API, and
  exposes `GET /health` as the container health check.
- `services/api/scripts/seed_demo.py` powers the compose `seed-demo` service for
  explicit demo seeding.

Goal 29 adds explicit environment configuration:

- `return_play.config.ReturnPlaySettings` centralizes typed backend settings.
- `create_runtime_app()` fails fast when `RETURN_PLAY_ENV=production` is missing
  required production values.
- `.env.example` documents local placeholders without committed secrets.

Goal 30 adds the observability baseline:

- `return_play.observability` adds request IDs and structured request logs.
- `GET /ready` reports application readiness.
- `GET /metrics` exposes low-cardinality runtime counters.
- `RETURN_PLAY_ERROR_TRACKING_DSN` enables the current error-capture seam.

Goal 31 adds backup and recovery operations:

- `scripts/backup/backup-postgres.ps1` creates a logical compose Postgres
  backup.
- `scripts/backup/restore-postgres.ps1` restores a backup behind an explicit
  confirmation phrase.
- `scripts/backup/restore-drill.ps1` proves backup and restore behavior in a
  disposable local/CI database.
- `docs/operations/backups-and-recovery.md` defines RPO/RTO targets and the
  verification checklist.

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

Alembic uses `RETURN_PLAY_DATABASE_URL` when it is set. Otherwise it falls back
to the URL in `alembic.ini`.

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

## Production Startup Validation

When `RETURN_PLAY_ENV=production`, API startup requires:

```text
RETURN_PLAY_DATABASE_URL=<database-url>
RETURN_PLAY_AUTH_MODE=token
RETURN_PLAY_AUTH_SECRET=<32-plus-character-signing-secret>
RETURN_PLAY_CORS_ORIGINS=https://app.example.com
```

Production startup rejects trusted local-header auth and the local login
provider.

## Observability

Every response includes `x-request-id`. The API emits JSON request logs through
the `return_play.requests` logger and exposes:

```text
GET /health
GET /ready
GET /metrics
```
