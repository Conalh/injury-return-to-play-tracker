# Injury Return-To-Play Tracker

**A safety-first workflow tracker for staged return-to-play decisions.**
Clinicians and athletic trainers get one place to track the athlete, injury
case, return-plan phases, symptom response, functional tests, workload
tolerance, readiness signals, limited share views, PDF reports, and the named
human decisions behind clearance.

This is not a diagnostic or automatic-clearance system. It is an evidence binder
and workflow surface: the product can show what is known, what is missing, what
changed, and who made the decision, but it must never diagnose an injury,
recommend treatment, override a clinician, hide red flags, or encourage
participation through worsening symptoms.

```text
Athlete roster + injury case
        |
        v
Staged return-plan template ----> case phases + milestone gates
        |                                      |
        v                                      v
Symptoms + functional tests + workload ----> readiness review
        |                                      |
        v                                      v
Named clearance decision <---- audit log + PDF report
        |
        v
Limited coach / athlete / guardian share view
```

## Current Status

The project is a local production-path build, currently through Goal 21 of the
ignored production roadmap. It is not hosted yet.

Live in the repo:

- FastAPI workflow API for athletes, injury cases, templates, evidence,
  readiness, named clearance decisions, limited share links, PDF reports, audit
  logs, and demo seeding.
- Authentication foundation with explicit local-header mode, HMAC bearer-token
  mode, `/api/me`, local login/logout session endpoints, and token-mode tests.
- Central role-to-permission matrix with route dependencies and repository
  service guards for protected workflow actions.
- Admin organization and user management for organization setup, user
  invitations, role changes, deactivation, and organization audit events.
- API-backed frontend data fetching with explicit demo fallback mode and
  Playwright coverage against a live FastAPI test server.
- Clinician case creation UI for athlete intake, injury case creation, staged
  template application, validation errors, and athlete profile edits.
- Template builder UI for listing templates, creating staged phases and
  milestones, editing as a new version, archiving inactive plans, and applying
  active templates to cases.
- Evidence entry UI on case detail for symptom logs, functional tests, workload
  sessions, and milestone evidence updates with audit events.
- Human clearance decision UI for hold, advance, full clearance, and close-case
  decisions with required rationale, restrictions, named attribution, and audit
  events.
- Share management UI on case detail for creating limited coach, athlete, or
  guardian links, copying the share URL, revoking links, and reviewing audit
  events.
- Athlete portal for token-scoped current phase, assigned activities,
  instructions, clinician message, non-diagnostic language, and symptom
  check-ins without clinician-only data exposure.
- SQLAlchemy repository path selected by `RETURN_PLAY_DATABASE_URL`, with the
  in-memory repository retained for local/demo tests.
- Repository boundary package under `return_play.repositories`, split into
  athlete, case, template/plan, evidence, readiness, share/report/audit, and
  demo seed surfaces.
- Next.js clinician dashboard with roster, case detail, evidence panels,
  readiness review, clearance panel, and limited shared status view.
- Backend pytest coverage and frontend Playwright coverage for the current
  workflow surface.

Still deferred:

- Hosted identity-provider integration and token revocation.
- Production deployment, backups, monitoring, and compliance review package.

## Run It Locally

### API

```powershell
cd services/api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .[dev]
.\.venv\Scripts\python.exe -m uvicorn return_play.api:app --reload
```

Open `http://127.0.0.1:8000/health`.

By default the API uses the in-memory repository. To run the persistent path,
set:

```powershell
$env:RETURN_PLAY_DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/return_play"
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe -m uvicorn return_play.api:app --reload
```

The default auth mode is `dev_headers`, which accepts the local request-context
headers used by the tests and demo seed. To run the bearer-token path:

```powershell
$env:RETURN_PLAY_AUTH_MODE="token"
$env:RETURN_PLAY_AUTH_SECRET="<long-random-secret>"
```

### Web

```powershell
cd apps/web
npm install
npm run dev
```

Open `http://127.0.0.1:3217`.

The web app defaults to local demo data. Set `RETURN_PLAY_DATA_MODE=api` or
`RETURN_PLAY_DATA_MODE=api-demo` plus `RETURN_PLAY_API_BASE_URL` to render from
FastAPI.

## Demo Seed

With the API running, seed the Riley Chen local workflow:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/demo/seed `
  -Headers @{
    "x-actor-id" = "clinician_demo"
    "x-actor-role" = "clinician"
    "x-organization-id" = "org_demo"
  }
```

The seed covers a synthetic athlete, injury case, staged return plan, milestone
status, symptom logs, functional tests, workload sessions, clinician note, hold
decision, limited share link, readiness signals, PDF report, and audit events.

## Architecture

```text
apps/web
  Next.js App Router + TypeScript + Tailwind
  /                  clinician roster dashboard
  /cases/[id]        case detail, evidence, readiness, clearance
  /share/[token]     limited non-clinical status view

services/api
  FastAPI app factory + route surface
  auth.py            local request-context role gates
  models.py          Pydantic request contracts
  db.py              SQLAlchemy metadata
  repositories/      in-memory + SQLAlchemy workflow repositories
  readiness.py       conservative readiness signal builder
  reports.py         PDF report generation
  demo.py            synthetic workflow seed
  alembic/           migration history

packages/shared
  Reserved for shared contracts if both app surfaces genuinely need them.
```

The API exposes one workflow surface and can run against either repository:

- `InMemoryWorkflowRepository` for fast local tests and demo defaults.
- `SqlAlchemyWorkflowRepository` for persistent runtime behavior.

Compatibility shims keep the earlier `return_play.repository` and
`return_play.sql_repository` import paths working while new code imports from
`return_play.repositories`.

## Safety Model

Return-to-play decisions are high-stakes human decisions. The current safety
contract is:

- Protected API routes require local request-context headers:
  `x-actor-id`, `x-actor-role`, and `x-organization-id` only in explicit
  development-header mode.
- Token mode ignores trusted identity headers and builds request context from a
  verified bearer token.
- Clinical workflows are limited to clinician, athletic trainer, and admin
  roles until the production role matrix lands.
- Organization IDs scope roster, template, case, evidence, readiness,
  report, share-management, and audit-log access.
- Clearance decisions require a named actor and rationale.
- Readiness responses explicitly include `can_auto_clear: false`.
- Shared pages use non-diagnostic language and exclude symptom detail, guardian
  contact, and the full clinical record.

## Tests

Backend:

```powershell
cd services/api
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\alembic.exe heads
```

Frontend:

```powershell
cd apps/web
npm test
npm run build
npm audit --audit-level=high
```

Current coverage includes API contracts, schema contracts, migrations, clinician
workflow behavior, evidence capture, readiness signals, privacy and permission
checks, share/report/audit behavior, demo seed validation, persistent repository
restart behavior, repository-boundary contracts, and browser coverage for the
dashboard, API-backed case creation, template builder, evidence entry, clearance
decisions, share management, athlete portal, case detail, and limited share
page.

## Documentation

- [services/api/README.md](services/api/README.md): backend setup, scope, demo
  seed, and migration commands.
- [apps/web/README.md](apps/web/README.md): frontend scope and local commands.
- [docs/README.md](docs/README.md): documentation index.
- [docs/product/product-spec.md](docs/product/product-spec.md): safety-first
  product specification.
- [docs/product/safety-and-compliance-notes.md](docs/product/safety-and-compliance-notes.md):
  safety, privacy, and compliance notes.
- [docs/product/permission-matrix.md](docs/product/permission-matrix.md):
  current role-to-permission matrix and enforcement points.
- [docs/foundation/project-foundation.md](docs/foundation/project-foundation.md):
  initial repo and tooling direction.
- [docs/foundation/goal-roadmap.md](docs/foundation/goal-roadmap.md): original
  staged creation roadmap. Some later production-path decisions now live in the
  ignored local roadmap.
