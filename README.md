# Injury Return-To-Play Tracker

[![CI](https://github.com/Conalh/injury-return-to-play-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/Conalh/injury-return-to-play-tracker/actions/workflows/ci.yml)
[![Security Baseline](https://github.com/Conalh/injury-return-to-play-tracker/actions/workflows/security.yml/badge.svg)](https://github.com/Conalh/injury-return-to-play-tracker/actions/workflows/security.yml)
[![python](https://img.shields.io/badge/python-3.11-blue)](services/api/pyproject.toml)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)](apps/web/package.json)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688?logo=fastapi&logoColor=white)](services/api/pyproject.toml)
[![Postgres](https://img.shields.io/badge/Postgres-16-336791?logo=postgresql&logoColor=white)](compose.yml)
[![Playwright](https://img.shields.io/badge/Playwright-covered-2EAD33?logo=playwright&logoColor=white)](apps/web/playwright.config.ts)

**A safety-first control center for staged return-to-play decisions.**

Stagewise gives clinicians and athletic trainers one evidence binder for an
injury case: staged return-plan phases, symptom response, functional testing,
workload tolerance, readiness signals, limited family/coach views, PDF reports,
audit history, and the named human decision behind clearance.

It is not a diagnostic or automatic-clearance system. It does not diagnose
injuries, recommend treatment, override a clinician, hide red flags, or push an
athlete through worsening symptoms. Its job is to show what is known, what is
missing, what changed, and who made the decision.

> Built as a production-path local app: Next.js clinician workspace, FastAPI
> workflow API, Postgres-ready persistence, OIDC-ready auth, audit trails,
> limited share portals, and launch-gate operations docs. Hosting is still
> intentionally deferred.

```mermaid
flowchart LR
  Roster["Athlete roster"] --> Case["Injury case"]
  Case --> Plan["Staged return plan"]
  Plan --> Evidence["Symptoms<br/>tests<br/>workload"]
  Evidence --> Readiness["Readiness signals<br/>(explain-only)"]
  Readiness --> Decision["Named clinician<br/>decision"]
  Decision --> Outputs["Audit log<br/>PDF report<br/>limited share"]

  classDef intake fill:#0f172a,stroke:#1e293b,color:#e2e8f0
  classDef clinical fill:#f8fafc,stroke:#cbd5e1,color:#0f172a
  classDef safety fill:#fef3c7,stroke:#d97706,color:#78350f
  classDef output fill:#ecfeff,stroke:#0891b2,color:#164e63
  class Roster,Case,Plan intake
  class Evidence,Readiness clinical
  class Decision safety
  class Outputs output
```

**See also:** [docs/README.md](docs/README.md) for the full documentation map,
[docs/operations/production-launch-gate.md](docs/operations/production-launch-gate.md)
for the launch gate, and [docs/product/safety-and-compliance-notes.md](docs/product/safety-and-compliance-notes.md)
for the safety posture.

## Screenshots

Captured with Playwright against the seeded local demo workflow.

![Stagewise dashboard overview](docs/screenshots/dashboard-overview.png)

| Control center | Case detail |
| --- | --- |
| ![Control center dashboard](docs/screenshots/dashboard.png) | ![Case detail with readiness and phase gates](docs/screenshots/case-detail.png) |
| **Template builder** | **Limited coach share** |
| ![Template builder](docs/screenshots/templates.png) | ![Limited coach share view](docs/screenshots/share-view.png) |

## Project Snapshot

| Area | Current state |
| --- | --- |
| Product posture | Local production-path build, not hosted yet |
| Roadmap status | Implemented through Goal 53 of the ignored production roadmap |
| API | FastAPI workflow surface with in-memory and SQLAlchemy repositories |
| Web | Next.js Stagewise workspace plus limited coach, athlete, and guardian views |
| Safety stance | Explain-only readiness, named human clearance, non-diagnostic copy |
| Production blockers | Hosted identity tenant deployment, live smoke evidence, staging and production hosting |

The system is built around a conservative clinical record:

- Intake creates the athlete and injury case.
- A staged template defines phases and milestone gates.
- Evidence is captured as symptoms, functional tests, workload sessions,
  milestone updates, and clinician notes.
- Readiness signals explain missing evidence, symptom trends, workload
  tolerance, and clearance completeness.
- Clearance actions require a named actor, decision type, rationale, and
  restrictions when needed.
- Share links expose only audience-appropriate status for coaches, athletes,
  or guardians.

## Product Surface

| Surface | What it does |
| --- | --- |
| Clinician dashboard | Roster, active cases, status, current phase, and quick access to case work |
| Case detail | Phase timeline, milestones, evidence panels, readiness signals, decisions, shares, and audit trail |
| Template builder | Create, version, archive, and apply staged return-plan templates |
| Evidence entry | Record symptoms, functional tests, workload sessions, and milestone evidence |
| Clearance panel | Hold, advance, fully clear, or close a case with named rationale |
| Share management | Create, copy, revoke, and audit limited coach, athlete, or guardian links |
| Athlete portal | Token-scoped current phase, instructions, clinician message, and symptom check-ins |
| Guardian portal | Conservative participation status, restrictions, next review, and acknowledgment |
| Reports | PDF status report with evidence, restrictions, decision, audit metadata, and disclaimer |

## Production-Path Controls

| Control area | Implemented package |
| --- | --- |
| Authentication | Development headers, HMAC bearer tokens, login/logout, durable token revocation, OIDC adapter |
| Authorization | Central role-to-permission matrix plus route and repository guards |
| Privacy | Share-view field filtering, restricted response contracts, export/delete request plan |
| Audit | Sensitive writes, reads, reports, share activity, clearance decisions, immutable reads |
| Security baseline | Secure headers, CORS allowlist, request size limit, rate limits, secret scan, dependency scan |
| Accessibility | Axe-based Playwright smoke gate for key demo surfaces plus keyboard-focused workflow tests |
| Persistence | SQLAlchemy repository selected by `RETURN_PLAY_DATABASE_URL`; in-memory fallback for local/demo |
| Operations | Environment contract, observability, backup/restore drill, beta readiness, launch gate |
| Identity rollout | OIDC config, tenant checklist, MFA/password policy, claim mapping, smoke-test evidence plan |
| CI maintenance | Required checks, Dependabot updates, Node.js 24 GitHub Actions runtime opt-in |

## What Is Still Deferred

Broad production use remains blocked until these are completed outside the
current local build:

- Hosted identity-provider tenant deployment.
- Live identity smoke evidence in the target environment.
- Staging deployment.
- Production deployment.
- Legal/compliance signoff for the exact customer and data posture.

## Run It Locally

### API

```powershell
cd services/api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .[dev]
.\.venv\Scripts\python.exe -m uvicorn return_play.api:app --reload
```

Open:

```text
http://127.0.0.1:8000/health
```

The default repository is in-memory. To use Postgres-backed persistence:

```powershell
$env:RETURN_PLAY_DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/return_play"
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe -m uvicorn return_play.api:app --reload
```

The default auth mode is `dev_headers`, intended for local development and
tests. To run the local bearer-token path:

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

Open:

```text
http://127.0.0.1:3217
```

The web app defaults to local demo data. API-backed local mode uses:

```powershell
$env:RETURN_PLAY_DATA_MODE="api-demo"
$env:RETURN_PLAY_API_BASE_URL="http://127.0.0.1:8000"
$env:RETURN_PLAY_ACTOR_ID="clinician_demo"
$env:RETURN_PLAY_ACTOR_ROLE="clinician"
$env:RETURN_PLAY_ORGANIZATION_ID="org_demo"
npm run dev
```

### Browser Test Harness

Playwright uses a combined local harness:

```powershell
cd apps/web
npm test
```

That script starts FastAPI at `http://127.0.0.1:8015` and Next.js at
`http://127.0.0.1:3227`.

## Demo Seed

With the API running, seed the Riley Chen synthetic workflow:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/demo/seed `
  -Headers @{
    "x-actor-id" = "clinician_demo"
    "x-actor-role" = "clinician"
    "x-organization-id" = "org_demo"
  }
```

The seed includes an athlete, injury case, staged return plan, milestone
status, symptom logs, functional tests, workload sessions, clinician note, hold
decision, limited share link, readiness signals, PDF report, and audit events.

## Architecture

```text
apps/web
  Next.js App Router + TypeScript + Tailwind
  /                  clinician roster dashboard
  /cases/[id]        case detail, evidence, readiness, clearance, shares
  /templates         staged return-plan template builder
  /share/[token]     limited coach, athlete, or guardian status view

services/api
  FastAPI app factory + route surface
  auth.py            dev headers, HMAC tokens, OIDC verification, logout
  permissions.py     role-to-permission matrix
  audit.py           audit event taxonomy
  privacy.py         field filters + data-control policy hooks
  security.py        headers, CORS, size limits, rate limits
  observability.py   request IDs, structured logs, readiness, metrics
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

Return-to-play decisions are high-stakes human decisions. The repository keeps
these boundaries explicit:

- Development-header auth is local only; token mode ignores trusted identity
  headers and builds request context from verified bearer tokens.
- Persistent deployments store hashed revoked token IDs so logout revocation
  survives API restarts and can be shared by API workers.
- OIDC provider mode validates RS256 tokens against configured issuer,
  audience, JWKS, role claim, organization claim, subject, expiration, and token
  ID.
- Organization IDs scope roster, template, case, evidence, readiness, reports,
  share management, and audit-log access.
- Readiness responses explain evidence status and always include
  `can_auto_clear: false`.
- Clearance decisions require a named actor and rationale.
- Limited share views use explicit data contracts and exclude raw clinical
  records that do not belong to the audience.
- API request logs are structured and intentionally avoid clinical payloads.

## Validation

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

CI currently covers backend tests, migration head checks, web build, Playwright
browser coverage, Docker compose build validation, backup restore drill,
dependency audit, and secret scan.

## Documentation Map

Start here:

- [docs/README.md](docs/README.md): full documentation index.
- [services/api/README.md](services/api/README.md): API setup, scope, demo
  seed, and migration commands.
- [apps/web/README.md](apps/web/README.md): web app scope, local modes, and
  frontend commands.

Product documents:

- [Product specification](docs/product/product-spec.md)
- [Permission matrix](docs/product/permission-matrix.md)
- [Privacy controls](docs/product/privacy-controls.md)
- [Security baseline](docs/product/security-baseline.md)
- [Legal/compliance review package](docs/product/legal-compliance-review-package.md)
- [Usability review](docs/product/usability-review.md)

Operations documents:

- [Beta readiness](docs/operations/beta-readiness.md)
- [Production launch gate](docs/operations/production-launch-gate.md)
- [Auth token revocation](docs/operations/auth-token-revocation.md)
- [Hosted identity OIDC](docs/operations/hosted-identity-oidc.md)
- [Identity provider tenant rollout](docs/operations/identity-provider-tenant-rollout.md)
- [Required CI checks](docs/operations/ci-required-checks.md)
- [Dependency update automation](docs/operations/dependency-update-automation.md)
- [GitHub Actions runtime readiness](docs/operations/github-actions-runtime-readiness.md)
- [Environment configuration](docs/operations/environment-configuration.md)
- [Observability](docs/operations/observability.md)
- [Backups and recovery](docs/operations/backups-and-recovery.md)

## License

MIT. See [LICENSE](LICENSE).
