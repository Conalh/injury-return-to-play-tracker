# Injury Return-To-Play Tracker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a clinician- and coach-friendly return-to-play tracker that maps an injured athlete through staged milestones, symptoms, functional tests, workload progression, clearance gates, and shared reports.

**Architecture:** A Next.js dashboard talks to a FastAPI API. Postgres stores athletes, injuries, return plans, milestones, tests, symptom logs, workload sessions, clinician notes, and clearance decisions. A rules engine checks readiness evidence and highlights missing gates, but never auto-clears an athlete.

**Tech Stack:** Next.js, TypeScript, Tailwind, TanStack Query, FastAPI, Python, Pydantic, Postgres, pytest, Playwright, optional PDF export.

---

## Product Thesis

Return-to-play decisions are high-stakes, messy, and distributed across people. Athletes, clinicians, trainers, coaches, and parents may all hold pieces of the picture.

This product should not replace clinical judgment. It should make the process visible:

- What phase is the athlete in?
- What milestones have been met?
- What symptoms or red flags remain?
- What functional tests were performed?
- What workload has been tolerated?
- Who cleared what, and when?
- What evidence supports the next progression?

The product is an evidence binder and workflow tracker, not a medical device.

## Target Users

Primary users:

- Physical therapists.
- Athletic trainers.
- Sports medicine clinicians.

Secondary users:

- Strength coaches.
- Team coaches with limited permissions.
- Athletes and guardians viewing assigned tasks and progress.

## Safety Boundaries

This product must never:

- Diagnose an injury.
- Recommend a medical treatment.
- Clear an athlete automatically.
- Override a clinician.
- Hide red flags.
- Encourage play through worsening symptoms.

The product can:

- Track clinician-defined plans.
- Track symptoms and function.
- Highlight missing evidence.
- Generate reports.
- Require explicit human clearance.
- Provide templates that clinicians can edit.

## Core Product Loop

1. Clinician creates athlete profile.
2. Clinician creates injury case.
3. Clinician selects or builds a return-to-play template.
4. Athlete logs symptoms and completion of assigned activities.
5. Clinician records functional tests and milestone outcomes.
6. System computes evidence completeness and flags missing gates.
7. Clinician advances phase or holds phase with notes.
8. Report is shared with athlete, coach, or guardian.

## V1 Scope

Included:

- Single organization account.
- Athlete roster.
- Injury case creation.
- Return plan templates.
- Phase and milestone tracking.
- Symptom logs.
- Functional test logs.
- Workload/session logs.
- Human clearance records.
- Coach/athlete read-only share link.
- PDF report.
- Demo data.

Excluded from V1:

- EHR integration.
- Billing.
- Insurance documentation.
- Wearable integrations.
- Sport-specific force-plate integrations.
- Automated medical protocols.
- Emergency triage.

## Product Surfaces

### Roster

Purpose: Show every athlete under care and who needs attention.

Sections:

- Athlete name and sport.
- Active injury.
- Current phase.
- Days in phase.
- Latest symptom status.
- Missing gate count.
- Next required action.

### Injury Case Detail

Purpose: Central workspace for one injury.

Sections:

- Injury summary.
- Phase timeline.
- Current phase gates.
- Symptom trend.
- Functional tests.
- Workload progression.
- Notes.
- Clearance panel.
- Share/report actions.

### Plan Template Builder

Purpose: Let clinicians define staged return plans.

Fields:

- Template name.
- Injury category.
- Phases.
- Milestones per phase.
- Required tests.
- Symptom rules.
- Workload progression rules.
- Required clearance roles.

### Athlete Portal

Purpose: Give the athlete only what they need.

Sections:

- Current phase.
- Assigned activities.
- Symptom check-in.
- Today's instructions.
- What must happen before progressing.
- Clinician messages.

### Coach/Guardian Share

Purpose: Share status without oversharing medical detail.

Sections:

- Current participation status.
- Allowed activities.
- Restricted activities.
- Next review date.
- Clearance status.
- Clinician note.

## Data Model

### Organization

- id
- name
- timezone
- created_at

### User

- id
- organization_id
- email
- name
- role: clinician, athletic_trainer, coach, athlete, guardian, admin
- created_at

### Athlete

- id
- organization_id
- name
- date_of_birth
- sport
- position
- guardian_contact
- active

### InjuryCase

- id
- organization_id
- athlete_id
- title
- injury_category
- body_region
- side
- date_of_injury
- status: active, paused, cleared, closed
- clinician_owner_id
- summary
- created_at
- updated_at

### ReturnPlanTemplate

- id
- organization_id
- name
- injury_category
- description
- created_by
- version
- active

### ReturnPlanPhase

- id
- template_id
- name
- order_index
- objective
- minimum_days
- exit_summary

### Milestone

- id
- phase_id
- title
- kind: symptom, function, strength, range_of_motion, workload, clinician_review, other
- required
- instructions

### CasePhaseStatus

- id
- injury_case_id
- phase_id
- status: locked, current, passed, held
- started_at
- completed_at
- clinician_note

### MilestoneResult

- id
- injury_case_id
- milestone_id
- status: not_started, passed, failed, waived
- recorded_by
- recorded_at
- notes
- evidence_json

### SymptomLog

- id
- injury_case_id
- athlete_id
- date
- pain: 0 to 10
- swelling: none, mild, moderate, severe
- confidence: 1 to 5
- notes

### FunctionalTest

- id
- injury_case_id
- name
- test_date
- result_value
- unit
- side_to_side_difference_percent
- passed
- recorded_by
- notes

### WorkloadSession

- id
- injury_case_id
- date
- activity
- duration_minutes
- intensity: 1 to 10
- symptom_response
- completed
- notes

### ClearanceDecision

- id
- injury_case_id
- phase_id
- decision: advance, hold, clear_full, close_case
- decided_by
- decided_at
- rationale
- restrictions

### ShareToken

- id
- injury_case_id
- audience: athlete, coach, guardian
- token_hash
- expires_at
- revoked_at

## Readiness Engine

The readiness engine answers: "What evidence is missing or concerning before this athlete progresses?"

It must not answer: "Is the athlete medically safe to play?"

### Signal: Missing Required Milestones

Inputs:

- Current phase milestones.
- Milestone results.

Output:

- Count of required milestones not passed or waived.
- Names of missing items.

### Signal: Symptom Worsening

Inputs:

- Last 7 symptom logs.
- Pain, swelling, confidence.

Rules:

- Mild concern: pain increased by 2 points since previous log.
- Moderate concern: pain >= 5 or swelling moderate.
- Severe concern: swelling severe or pain >= 7.

Output:

- Hold recommendation for clinician review.
- No auto-progression.

### Signal: Workload Tolerance

Inputs:

- Workload sessions.
- Symptom response.

Rules:

- Stable: completed planned sessions with no symptom increase.
- Watch: completed with mild symptom increase.
- Concern: failed sessions or symptom increase after two sessions.

### Signal: Clearance Completeness

Inputs:

- Required clearance roles.
- Clearance decisions.

Output:

- Missing clinician decision.
- Missing athletic trainer decision.
- Missing guardian acknowledgment when configured.

## Recommendation Types

Allowed:

- "Review symptoms before advancing."
- "Functional test missing."
- "Workload progression incomplete."
- "Clinician clearance required."
- "Athlete report ready to share."
- "Hold phase until clinician updates milestone."

Not allowed:

- "Athlete is safe to play."
- "Clear athlete automatically."
- "Ignore symptom increase."
- "Progress because minimum days elapsed."

## API Surface

### Roster and Cases

- `GET /api/athletes`
- `POST /api/athletes`
- `GET /api/athletes/{athlete_id}`
- `PATCH /api/athletes/{athlete_id}`
- `POST /api/injury-cases`
- `GET /api/injury-cases/{case_id}`
- `PATCH /api/injury-cases/{case_id}`

### Plans and Milestones

- `GET /api/templates`
- `POST /api/templates`
- `GET /api/templates/{template_id}`
- `POST /api/injury-cases/{case_id}/apply-template`
- `GET /api/injury-cases/{case_id}/phases`
- `PATCH /api/injury-cases/{case_id}/milestones/{milestone_id}`

### Logs and Tests

- `POST /api/injury-cases/{case_id}/symptoms`
- `GET /api/injury-cases/{case_id}/symptoms`
- `POST /api/injury-cases/{case_id}/functional-tests`
- `GET /api/injury-cases/{case_id}/functional-tests`
- `POST /api/injury-cases/{case_id}/workload-sessions`
- `GET /api/injury-cases/{case_id}/workload-sessions`

### Readiness and Clearance

- `GET /api/injury-cases/{case_id}/readiness`
- `POST /api/injury-cases/{case_id}/clearance`
- `GET /api/injury-cases/{case_id}/report`
- `POST /api/injury-cases/{case_id}/share`
- `GET /api/share/{token}`

## Frontend Component Map

- `app/page.tsx`: roster.
- `app/cases/[id]/page.tsx`: injury case detail.
- `app/templates/page.tsx`: template list.
- `app/templates/[id]/page.tsx`: template builder.
- `app/share/[token]/page.tsx`: read-only share.
- `components/phase-timeline.tsx`: phase progression.
- `components/milestone-checklist.tsx`: current gates.
- `components/symptom-trend.tsx`: symptom log chart.
- `components/functional-test-table.tsx`: test evidence.
- `components/workload-progression.tsx`: workload history.
- `components/clearance-panel.tsx`: human decision form.
- `components/readiness-card.tsx`: missing evidence summary.

## Backend Module Map

- `return_play/api.py`: FastAPI app.
- `return_play/models.py`: Pydantic schemas.
- `return_play/db.py`: repository helpers.
- `return_play/templates.py`: template lifecycle.
- `return_play/cases.py`: injury case workflow.
- `return_play/readiness.py`: missing-gate and concern signals.
- `return_play/reports.py`: PDF/share report.
- `return_play/demo.py`: demo roster and cases.

## Implementation Phases

### Phase 1: Roster and Cases

- [ ] Create organization, user, athlete, and injury case schema.
- [ ] Add roster CRUD.
- [ ] Add injury case CRUD.
- [ ] Add role-aware permissions.
- [ ] Seed demo roster.
- [ ] Test cross-organization isolation.

Exit criteria:

- A clinician can create athletes and injury cases.

### Phase 2: Plan Templates

- [ ] Create template schema.
- [ ] Create phase schema.
- [ ] Create milestone schema.
- [ ] Build template CRUD.
- [ ] Apply template to injury case.
- [ ] Test template versioning and phase order.

Exit criteria:

- A clinician can apply a staged plan to an injury case.

### Phase 3: Logs and Evidence

- [ ] Add symptom logs.
- [ ] Add functional test logs.
- [ ] Add workload session logs.
- [ ] Add milestone result updates.
- [ ] Add evidence JSON validation.
- [ ] Test symptom trends and milestone state transitions.

Exit criteria:

- The case detail page can show evidence attached to each phase.

### Phase 4: Readiness Engine

- [ ] Implement missing milestone signal.
- [ ] Implement symptom worsening signal.
- [ ] Implement workload tolerance signal.
- [ ] Implement clearance completeness signal.
- [ ] Return source facts for every signal.
- [ ] Test no auto-clear path exists.

Exit criteria:

- `GET /api/injury-cases/{case_id}/readiness` explains what blocks progression.

### Phase 5: Frontend Workflow

- [ ] Build roster.
- [ ] Build case detail.
- [ ] Build phase timeline.
- [ ] Build milestone checklist.
- [ ] Build symptom, test, and workload panels.
- [ ] Build clearance panel.

Exit criteria:

- A clinician can manage one injury case end to end from the browser.

### Phase 6: Sharing and Reporting

- [ ] Build athlete portal.
- [ ] Build coach/guardian share page.
- [ ] Add share token creation and revocation.
- [ ] Generate PDF report.
- [ ] Add audit log for share creation and clearance decisions.

Exit criteria:

- A clinician can share a controlled status summary without exposing the full medical record.

## Privacy and Safety

Required controls:

- Strong authentication.
- Role-based access.
- Organization isolation.
- Audit log for every clearance decision.
- Share tokens with expiration and revocation.
- Minimal coach/guardian view.
- Clear non-diagnostic language.
- No automated clearance.

If sold to clinics or providers, review HIPAA and business associate obligations before handling protected health information. If sold directly to teams outside covered-entity relationships, still treat injury data as highly sensitive and review FTC health app obligations.

## Success Metrics

- Clinician creates an injury case in under three minutes.
- Clinician can see current phase and missing gates at a glance.
- Athlete logs symptoms on at least 70 percent of assigned days.
- Reports reduce back-and-forth between clinician and coach.
- No user can progress a phase without an explicit human decision.

## Risks

- Product can accidentally imply medical clearance.
- Templates can become stale or too generic.
- Coaches may overuse limited share views.
- Legal obligations change based on customer type.
- Injury-specific protocols can explode scope.

Mitigations:

- Treat templates as editable workflow scaffolds.
- Require named human decisions.
- Keep coach view restrictive.
- Add legal review before healthcare sales.
- Start with generic phase/milestone infrastructure, then add specific templates.

## Reference Sources To Review During Build

- 2016 Bern return-to-sport consensus statement: https://bjsm.bmj.com/content/50/14/853
- Team Physician Consensus Statement 2023 update metadata: https://scholar.usuhs.edu/en/publications/team-physician-consensus-statement-return-to-sportreturn-to-play--2/
- AAOS team physician return-to-play decision consensus PDF: https://www.aaos.org/globalassets/about/bylaws-library/information-statements/1036-the-team-physician-and-the-return-to-play-decision---a-consensus-statement.pdf
- HHS health app developer resources: https://www.hhs.gov/hipaa/for-professionals/special-topics/health-apps/index.html
- FTC Health Breach Notification Rule guidance: https://www.ftc.gov/business-guidance/resources/complying-ftcs-health-breach-notification-rule-0
