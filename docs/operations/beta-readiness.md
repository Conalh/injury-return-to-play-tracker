# Beta Readiness

Status: Goal 36 operations package

This package defines the minimum controlled-beta operating model for the local
production-path product. It does not approve real athlete health data by itself.
Hosting remains deferred until staging and production deployment goals are
reopened.

Supporting controls:

- `docs/product/legal-compliance-review-package.md`
- `docs/product/usability-review.md`
- `docs/product/privacy-controls.md`
- `docs/product/security-baseline.md`
- `docs/operations/backups-and-recovery.md`
- `docs/operations/observability.md`
- `docs/operations/local-production-compose.md`
- `docs/operations/environment-configuration.md`
- `docs/operations/ci-required-checks.md`

## Beta Scope

Allowed beta posture:

- Controlled organization only.
- Named admin, clinician, and athletic trainer users only.
- Coach, athlete, and guardian access only through limited share views.
- Synthetic or explicitly approved pilot data only until counsel/compliance
  signs off on real athlete data.
- Return-to-play workflow tracking only: intake, staged plan, evidence entry,
  readiness review, named clearance decision, limited share, PDF report, audit
  review, and feedback capture.

Blocked beta posture:

- No public self-serve signup.
- No broad production launch.
- No unreviewed school/minor data collection.
- No automatic clearance, diagnosis, treatment recommendation, or emergency
  response claims.
- No direct database edits as a support path.
- No handling of real data without completed legal/compliance gate, approved
  customer agreement, subprocessor list, and incident owner.

## Beta Onboarding Checklist

Before beta organization access:

- Identify organization name, primary admin, primary clinician, backup
  clinician, and support contact.
- Confirm legal/compliance review status and whether the beta uses synthetic,
  de-identified, or approved real data.
- Confirm approved roles for every invited user.
- Confirm coach, athlete, and guardian share-link policy.
- Confirm data retention expectations and whether exports are allowed.
- Confirm incident contact path and expected response window.
- Confirm support hours and non-emergency disclaimer.
- Confirm which workflows are in scope: case creation, evidence entry,
  clearance decisions, share links, reports, audit review, athlete portal, and
  guardian portal.
- Confirm which workflows are out of scope: hosted identity-provider testing,
  production deployment, automated clearance, billing, integrations, and
  self-serve account management.

Setup steps:

- Run the configured API and web deployment target for the beta environment.
- Apply migrations before access.
- Create or verify organization admin access.
- Invite named clinician and athletic trainer users.
- Seed only approved demo or pilot data.
- Verify `/health`, `/ready`, and web dashboard load.
- Verify one clinician can create a case, add evidence, record a hold decision,
  create and revoke a limited share link, download a report, and filter audit
  history.
- Save the beta start date, contacts, approved data posture, and known
  limitations in the beta record.

## Feedback Capture Process

Feedback channels:

- Product feedback: structured issue or feedback form.
- Workflow blocker: support ticket with `beta-blocker` label.
- Safety/privacy concern: immediate incident triage path.
- Bug report: reproducible steps, actor role, browser, timestamp, case ID if
  allowed, expected result, actual result, and screenshot if safe to share.

Triage levels:

| Level | Description | Initial response target | Owner |
| --- | --- | --- | --- |
| P0 | Safety, privacy, security, data exposure, or inability to stop risky access | Same day | Incident owner |
| P1 | Clinician cannot complete case, evidence, decision, share, or report workflow | 1 business day | Product/engineering owner |
| P2 | Workflow friction, unclear copy, mobile layout issue, or accessibility issue | 2 business days | Product owner |
| P3 | Enhancement request or future integration idea | Weekly review | Product owner |

Feedback handling rules:

- Do not ask users to send raw clinical data through general feedback.
- If a screenshot contains sensitive information, move the item into the
  incident/privacy handling path.
- Keep product enhancement requests separate from launch blockers.
- Close the loop with the reporter when a blocker is resolved or deferred.
- Convert repeated P2 issues into beta polish backlog items.

## Known Limitations

Current known limitations:

- Hosted identity-provider integration and durable multi-instance token
  revocation are deferred. Local HMAC logout revocation exists for the
  production-path API, but it is process-local.
- Staging and production deployment are deferred.
- Production secret management, distributed rate limiting, WAF rules, and
  platform-level monitoring are not yet configured.
- Retention, export, deletion, and breach-response workflows are documented as
  policy hooks and runbooks, not fully automated production operations.
- Share links are token-scoped and expiring/revocable, but not full
  authenticated coach/athlete/guardian accounts.
- The search affordance in the control-center shell is not a full command
  palette yet.
- Sidebar queue counts are static UI values until queue APIs are added.
- Empty/error panels still need full control-center visual restyling.
- Automated contrast checks are not yet in CI.
- Legal documents, signed BAA or non-BAA decision memo, and subprocessor list
  are not included in this repository.

Allowed workaround policy:

- Use only documented UI/API workflows.
- Use PDF reports only for clinician-reviewed exports.
- Use limited share links only for approved audiences.
- Revoke share links immediately when access is no longer appropriate.
- Escalate privacy/security concerns instead of working around them.

## Support Runbook

Routine support intake:

1. Confirm the requester, organization, role, and contact path.
2. Classify the request as product feedback, workflow blocker, bug, access
   issue, privacy concern, security concern, or incident.
3. Ask for non-sensitive reproduction details.
4. Check whether the issue is already listed in Known Limitations.
5. Reproduce in a safe local or approved beta environment when possible.
6. Record the resolution, workaround, or escalation decision.

Access support:

- Verify the actor and organization before discussing any case.
- Do not disclose clinical details to coach, athlete, or guardian contacts
  outside the approved limited share surface.
- For lost or inappropriate share access, revoke the link and create a new one
  only if the clinician approves.
- For user role mistakes, route to the organization admin workflow.

Clinical workflow support:

- Case creation issues: verify required fields, active template availability,
  and validation messages.
- Evidence issues: verify the current phase, evidence type, required fields,
  and audit entry creation.
- Clearance issues: verify decision type, rationale, restrictions, current
  phase, and named actor.
- Report issues: verify report permission and case status before regenerating.
- Audit issues: verify event type and actor filters before escalating.

Operational support:

- Use `docs/operations/local-production-compose.md` for local production-shaped
  startup.
- Use `docs/operations/environment-configuration.md` for runtime settings.
- Use `docs/operations/observability.md` for request IDs, logs, `/ready`, and
  `/metrics`.
- Use `docs/operations/backups-and-recovery.md` for restore drills and recovery
  expectations.

## Incident Response Starter Plan

Incident triggers:

- Suspected unauthorized access to clinical or share data.
- Share link sent to the wrong audience.
- Report exported or shared incorrectly.
- Missing or inaccurate audit events for sensitive access.
- Data corruption, data loss, or failed restore.
- Security alert, secret exposure, dependency vulnerability, or suspicious API
  traffic.
- User reports that the product implied automatic clearance or medical advice.

Immediate response:

1. Stop further exposure if possible: revoke share link, deactivate user, or
   disable affected workflow.
2. Preserve facts: request ID, actor ID, organization ID, case/share ID,
   timestamp, route, browser, and screenshots if safe.
3. Classify severity and assign an incident owner.
4. Notify the organization contact if required by the beta agreement or
   legal/compliance direction.
5. Record timeline, decisions, and containment actions.
6. Decide whether legal/compliance review, breach-notification review, or
   security disclosure is required.
7. Write a post-incident note with root cause, corrective action, and follow-up
   owner.

Do not:

- Delete logs or audit records to hide an issue.
- Ask users to email raw sensitive health data for debugging.
- Reopen revoked share links without clinician approval.
- Promise regulatory conclusions without counsel/compliance review.
- Treat this product as emergency-response infrastructure.

## Beta Organization Workflow

A beta organization can operate without direct database or developer access when
these paths are available:

- Admin creates or manages invited users through the organization user workflow.
- Clinician creates athlete and injury case records through the web UI.
- Clinician applies an active return-plan template through case creation.
- Clinician records symptoms, functional tests, workload, and milestone
  evidence through case detail.
- Clinician reviews readiness signals with visible non-automatic-clearance
  language.
- Clinician records named hold, advance, full-clearance, or close-case decisions
  with rationale.
- Clinician creates, copies, and revokes limited share links.
- Athlete and guardian audiences use token-scoped portal actions when approved.
- Clinician downloads PDF reports and reviews audit events from case detail.
- Support uses documented logs, health checks, runbooks, and feedback triage
  instead of editing the database directly.

Current automated proof:

- `apps/web/tests/case-creation.spec.ts`
- `apps/web/tests/evidence-entry.spec.ts`
- `apps/web/tests/clearance-decision.spec.ts`
- `apps/web/tests/share-management.spec.ts`
- `apps/web/tests/athlete-portal.spec.ts`
- `apps/web/tests/guardian-portal.spec.ts`
- `apps/web/tests/report-download.spec.ts`
- `apps/web/tests/audit-log-ui.spec.ts`
- `apps/web/tests/usability-review.spec.ts`
- `services/api/tests/test_beta_readiness_package.py`

## Launch Gate

Controlled beta remains blocked until:

- Legal/compliance review either approves the beta data posture or limits beta
  to synthetic/de-identified data.
- Terms, privacy notice, BAA or non-BAA decision memo, and subprocessor list are
  available for the selected beta customer type.
- A named product owner, support owner, incident owner, and engineering owner
  are assigned.
- The organization onboarding checklist is completed.
- Known limitations are shared with the beta organization.
- Feedback and incident channels are live.
- CI is green, backup restore drill passes, and the local production-shaped
  runbook has been exercised for the selected beta environment.
- No P0/P1 safety, privacy, security, or core workflow blockers remain open.
