# Goal Roadmap

This roadmap converts the original `PLAN.md` into project-creation goals.

## Goal 0: Product And Repo Foundation

Set up the repo and documentation foundation before application code exists.

Deliverables:

- README.
- `.gitignore`, `.editorconfig`, `.env.example`.
- Documentation index.
- Planned folder boundaries for web, API, and shared contracts.
- Explicit local tooling assumptions.

## Goal 1: Safety-First Product Spec

Turn the product idea into a tighter safety-first spec that can guide
implementation.

Deliverables:

- Product spec.
- Safety and compliance notes.
- Explicit allowed/disallowed product behavior.
- Launch blockers for privacy, access control, auditability, and share links.

## Goal 2: Data Model And Backend Skeleton

Create the FastAPI app, Pydantic schemas, database migrations, and repository
layer for organizations, users, athletes, injury cases, templates, phases,
milestones, logs, tests, workload sessions, clearances, and share tokens.

Status: complete. The backend skeleton, request contracts, SQLAlchemy
metadata, and Alembic baseline exist. Repository methods and CRUD behavior are
deferred to the clinician MVP workflow.

## Goal 3: Clinician MVP Workflow

Build the minimum useful clinician loop: roster, athlete creation, injury case
creation, template application, current phase display, milestone status, and
clinician notes.

Status: complete. The API now supports this workflow through an in-memory
repository seam, with SQLAlchemy metadata and migrations updated for clinician
notes. Postgres-backed repositories remain deferred.

## Goal 4: Evidence Capture

Add symptom logs, functional test logs, workload sessions, and milestone
evidence.

Status: complete. The API can create and list symptom logs, functional tests,
and workload sessions for an injury case. Case detail responses include the
captured evidence collections. Runtime persistence remains in-memory until the
Postgres repository goal.

## Goal 5: Readiness Engine

Implement explain-only readiness signals for missing milestones, symptom
concerns, workload tolerance, and clearance completeness.

Status: complete. The API exposes an explain-only readiness endpoint that
returns missing milestone, symptom, workload, and clearance completeness signals
with source facts. It explicitly reports that auto-clearance is unavailable.

## Goal 6: Frontend Clinician Dashboard

Build the Next.js clinician dashboard around roster, case detail, phase
timeline, milestone checklist, symptom trend, test table, workload history,
readiness card, and clearance panel.

Status: complete. The local Next.js app provides the roster and case-detail
clinician dashboard with demo data, Playwright coverage, and responsive visual
checks. Live FastAPI integration remains deferred.

## Goal 7: Sharing And Reports

Add athlete, coach, and guardian views with limited information, expiring share
links, revocation, PDF reports, and audit logging.

Status: complete. The API can create expiring share tokens, return a limited
share payload, revoke tokens, generate a PDF status report, and record audit
events for share/report activity. The web app includes a demo coach share view
that intentionally omits clinical evidence detail and private contact data.

## Goal 8: Privacy, Permissions, And Audit Hardening

Harden authentication, role-based access, organization isolation, audit logs,
restricted share views, and non-diagnostic language.

Status: complete. Protected API routes now require an explicit local request
context, enforce clinician/athletic-trainer/admin roles, and scope reads and
writes to the request organization. Clearance decisions are named human records
with audit events, share-management routes are protected, shared views remain
token-limited, and share copy now states that the page is not medical
clearance. Production-grade identity and session/token verification remain
outside this local scaffold.

## Goal 9: Demo And Validation

Seed demo data and prove the complete workflow with pytest and Playwright.
