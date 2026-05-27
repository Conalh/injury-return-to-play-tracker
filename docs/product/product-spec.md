# Safety-First Product Spec

Status: accepted as Goal 1 baseline

## Product Position

The Injury Return-To-Play Tracker is a workflow and evidence tracker for staged
return-to-play decisions.

It helps clinicians and athletic trainers collect, organize, and explain:

- Current phase.
- Phase goals and gates.
- Symptom history.
- Functional test evidence.
- Workload tolerance.
- Human clearance decisions.
- Shareable participation status.

It does not make medical decisions. It does not determine whether an athlete is
safe to play. It makes the evidence state visible so qualified people can make
and document decisions.

## Primary Users

- Physical therapists.
- Athletic trainers.
- Sports medicine clinicians.

## Secondary Users

- Strength coaches.
- Team coaches with limited permissions.
- Athletes.
- Parents or guardians.
- Organization admins.

## Core Workflow

1. Clinician creates an athlete profile.
2. Clinician opens an injury case.
3. Clinician applies or builds a return-to-play plan.
4. Athlete logs assigned symptoms and activity completion.
5. Clinician records milestones, functional tests, and workload sessions.
6. Readiness engine reports missing evidence and concerning signals.
7. Clinician records a decision to advance, hold, clear, or close.
8. Clinician shares a limited report with athlete, coach, or guardian.

## V1 Product Scope

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
- Limited coach, athlete, and guardian share links.
- PDF report.
- Demo data.

Excluded:

- Diagnosis.
- Treatment recommendation.
- Emergency triage.
- Automated clearance.
- EHR integration.
- Billing.
- Insurance documentation.
- Wearable integrations.
- Sport-specific force-plate integrations.

## Product Surfaces

### Roster

Purpose: show every athlete under care and make attention-needed cases obvious.

Required information:

- Athlete name and sport.
- Active injury case.
- Current phase.
- Days in phase.
- Latest symptom status.
- Missing gate count.
- Next required action.

### Injury Case Detail

Purpose: provide the clinician workspace for one injury case.

Required sections:

- Injury summary.
- Phase timeline.
- Current phase gates.
- Symptom trend.
- Functional tests.
- Workload progression.
- Notes.
- Readiness card.
- Clearance panel.
- Share/report actions.

### Plan Template Builder

Purpose: let clinicians define editable staged plans.

Required fields:

- Template name.
- Injury category.
- Phases.
- Milestones per phase.
- Required tests.
- Symptom rules.
- Workload progression rules.
- Required clearance roles.

Templates are workflow scaffolds, not protocols that guarantee safe return.

### Athlete Portal

Purpose: give the athlete only the information and actions assigned to them.

Required sections:

- Current phase.
- Assigned activities.
- Symptom check-in.
- Today's instructions.
- What must happen before progression can be reviewed.
- Clinician messages.

### Coach/Guardian Share

Purpose: share participation status without exposing the full medical record.

Required sections:

- Current participation status.
- Allowed activities.
- Restricted activities.
- Next review date.
- Clearance status.
- Clinician note written for this audience.

The share view must not expose raw clinical notes, private symptom details, date
of birth, guardian contact details, internal audit logs, or unrelated injuries.

## Readiness Engine Contract

The readiness engine answers:

> What evidence is missing or concerning before this athlete progresses?

The readiness engine must not answer:

> Is this athlete medically safe to play?

Allowed outputs:

- Required milestone missing.
- Functional test missing.
- Symptom pattern needs clinician review.
- Workload progression incomplete.
- Clearance decision missing.
- Report ready to share.
- Phase held until clinician updates milestone.

Disallowed outputs:

- Athlete is safe to play.
- Athlete should return today.
- Athlete is cleared automatically.
- Ignore symptom increase.
- Progress because minimum days elapsed.

Every readiness output must include source facts, such as the specific milestone,
symptom log dates, workload sessions, or missing clearance roles that produced
the signal.

## Clearance Contract

Every phase advance, hold, full clearance, or case closure requires:

- Named user.
- Role.
- Timestamp.
- Decision.
- Rationale.
- Restrictions when relevant.

The product can make a decision form easy to complete, but it must not preselect
an advance or clearance decision.

## Language Rules

Use evidence and workflow language:

- "Missing evidence"
- "Ready for clinician review"
- "Clearance decision required"
- "Symptoms increased since previous log"
- "Workload progression incomplete"

Avoid medical certainty language:

- "Safe to play"
- "Recovered"
- "Healthy"
- "Passed medical clearance"
- "No risk"
- "Treatment recommendation"

## Data Sensitivity

Treat all injury, symptom, test, workload, clearance, and share-link data as
sensitive health-related information.

Before real athlete data is used, the application must have:

- Authentication.
- Role-based access.
- Organization isolation.
- Audit logs for clearance and sharing.
- Expiring and revocable share links.
- Encryption for secrets and production transport.
- Production privacy review.
- Legal review for HIPAA, FTC health app, state privacy, school, and minor
  athlete obligations.

## V1 Success Metrics

- Clinician creates an injury case in under three minutes.
- Clinician can see current phase and missing gates at a glance.
- Athlete logs symptoms on at least 70 percent of assigned days.
- Report reduces back-and-forth between clinician and coach.
- No phase progression can occur without explicit human decision metadata.

## Launch Blockers

The product cannot launch beyond fake demo data if any of these are missing:

- Human decision required for progression and clearance.
- Role-aware access.
- Organization isolation.
- Audit logging for clearance decisions.
- Limited share views.
- Share expiration and revocation.
- Non-diagnostic product language.
- Source facts for readiness signals.
- Clear demo-data-only mode during prototype work.

