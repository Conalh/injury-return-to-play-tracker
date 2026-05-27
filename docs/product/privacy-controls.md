# Privacy Controls And Data Minimization

Status: Goal 25 implementation notes

These controls are implementation guardrails, not legal advice. They define the
current product behavior before real athlete data is allowed.

## Field-Level Response Filtering

Limited share views are filtered through `return_play.privacy.filter_share_view`.
The allowed shared fields are:

- audience
- athlete_name
- sport
- injury_title
- current_phase
- participation_status
- allowed_activities
- restricted_activities
- next_review_date
- clearance_status
- clinician_note

Restricted share responses include a `data_contract` object that names the
audience, included fields, and fields excluded by policy. Blocked fields include
birth date, guardian contact, clinical notes, raw symptom logs, functional
tests, workload sessions, clearance decisions, phases, organization identifiers,
clinician ownership, token values, and token hashes.

## Share-View Data Contract

Coach, athlete, and guardian share views are token-scoped and minimal. They are
not clinical APIs. Restricted roles remain blocked from `/api/injury-cases/*`
clinical detail endpoints by the permission matrix.

The shared contract is intentionally conservative:

- Share views can explain current participation status and clinician-authored
  allowed or restricted activities.
- Share views cannot expose the clinical evidence record or private identifiers
  that are not required for the audience.
- Share reads are audited as `share_view_read`.
- Share links expire and can be revoked.

## Retention Policy Hooks

`GET /api/privacy/data-controls` exposes the current retention hooks:

- `case_retention_review`: review case records when a case closes or an
  organization policy changes.
- `expired_share_cleanup`: expire or revoke share tokens on expiration or manual
  revocation.
- `audit_log_retention_review`: retain audit logs unless a future organization
  retention policy says otherwise.

These are policy hooks only. Goal 25 does not delete clinical records
automatically.

## Export And Delete Request Plan

Export requests should:

- Verify the requesting organization and actor.
- Scope the request to a named athlete or case.
- Record a sensitive export audit event.
- Deliver only clinician-reviewed exports.

Delete requests should:

- Verify legal and clinical retention obligations first.
- Disable or revoke active share links.
- Queue the case-retention review hook.
- Record an organization audit event for final disposition.

## PHI And Health-Data Checklist

Before real data:

- Return the minimum necessary fields for the role and workflow.
- Keep restricted roles on token-scoped share views instead of clinical APIs.
- Audit share reads and sensitive exports.
- Keep share links expiring and revocable.
- Review HIPAA, FTC, BAA, retention, breach, and customer-contract obligations
  before production use.
