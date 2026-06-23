# Product Polish And Usability Review

Status: Goal 35 review packet

This review tightens the beta-facing clinical workflow without changing the
safety model. Hosting remains deferred; the review is based on the local
production-path app, the API-backed Playwright workflows, and the current
control-center UI.

## Review Scope

Reviewed surfaces:

- Clinician dashboard and roster triage.
- Case creation and template application.
- Case detail with evidence entry, readiness review, clearance decision, share
  management, PDF report access, and audit history.
- Athlete, guardian, and limited coach share views.
- Empty, error, unauthorized, and validation states already present in the app.

Out of scope for this goal:

- Hosted identity-provider integration.
- Staging and production deployment.
- Legal contract drafting.
- New clinical decision logic.

## Non-Diagnostic Copy Review

The current copy keeps the product framed as an evidence binder and workflow
surface:

- Dashboard safety note says Stagewise surfaces readiness signals and protocol
  completion, but does not clear athletes.
- Case detail risk banner says clinician review is required before advancement
  and the workflow never substitutes for a named clearance decision.
- Readiness rail says Stagewise does not auto-clear athletes.
- Share and portal surfaces use participation-status language instead of
  diagnostic detail.
- PDF and safety docs keep the non-diagnostic disclaimer in the product model.

No reviewed core page tells a clinician, athlete, guardian, or coach that the
system itself diagnoses, treats, or clears an athlete.

## Empty And Error States

Current states:

- Dashboard has an empty state for no active cases.
- Dashboard, case detail, case creation, template editing, athlete editing, and
  share views route unauthorized and API failure states through explicit state
  panels.
- Case creation, template creation, athlete editing, evidence entry, share
  creation, guardian acknowledgement, and athlete symptom check-in all expose
  validation or submission errors through inline UI.

Beta polish note: the next usability pass should make the shared `EmptyState`,
`ErrorState`, and `UnauthorizedState` visually match the control-center shell
instead of the earlier white-panel style.

## Mobile Layout Pass

Current automated coverage:

- `dashboard.spec.ts` checks dashboard and case detail at `390x844` and asserts
  no horizontal document overflow.
- `usability-review.spec.ts` repeats mobile checks while verifying safety copy
  and primary action access on dashboard and case detail.

Manual review focus for beta:

- Confirm dense roster tables remain scannable on phone width.
- Confirm share-management modal contents remain reachable on short screens.
- Confirm evidence entry forms are comfortable enough for repeated sideline
  entry.

## Accessibility Pass

Implemented guardrails:

- A keyboard skip link now lets users jump directly to the clinical workspace.
- Primary navigation has the `Primary clinical navigation` label.
- Case detail section navigation is labelled.
- Icon-only notification control has an accessible label.
- Form fields use visible labels.
- Validation panels and submission failures use alert-style presentation where
  the current component exposes errors.
- Decorative icons are marked `aria-hidden`.

Current automated coverage:

- `accessibility.spec.ts` runs axe-based WCAG smoke checks against the
  dashboard, case detail, template builder, and limited coach share view, and
  blocks serious or critical automated violations.
- `usability-review.spec.ts` verifies the skip link receives keyboard focus and
  moves focus to the clinical workspace.
- Existing Playwright tests use role and label locators across the core
  clinician and portal workflows, which gives practical coverage for many
  accessible names.

Beta polish note: extend automated accessibility coverage to every modal,
portal, and mobile breakpoint, and keep manual keyboard/screen-reader review in
the beta checklist.

## Clinician Workflow Timing Review

Observed core workflow from current Playwright coverage:

1. `case-creation.spec.ts`: clinician creates an athlete, creates an injury
   case, applies a return-plan template, and lands on case detail.
2. `evidence-entry.spec.ts`: clinician records symptoms, a functional test,
   workload, and milestone evidence from case detail.
3. `clearance-decision.spec.ts`: clinician records a named hold and full
   clearance decision with rationale.
4. `share-management.spec.ts`: clinician creates, copies, and revokes a limited
   share link.
5. `report-download.spec.ts`: clinician can find the PDF report download.
6. `audit-log-ui.spec.ts`: clinician can filter sensitive workflow audit reads.

The automated workflow path does not require developer commands, database
access, or hidden test hooks once the local API/web harness is running.

## Beta Polish Backlog

- Restyle shared empty/error/unauthorized panels into the new control-center
  visual system.
- Add active-route state to sidebar navigation after route taxonomy settles.
- Replace static shell counts with API-backed queue counts.
- Add a real command palette or remove the search affordance before beta.
- Expand automated accessibility checks beyond the current key-route smoke
  suite.
- Add a short clinician task-timing script for in-person review sessions.
- Add copy review for every modal and submitted-success state.

## Launch Gate

Goal 35 is complete for local beta-readiness evidence when:

- Core clinician workflow tests still pass.
- Mobile dashboard and case-detail no-overflow checks pass.
- Keyboard skip-link check passes.
- Non-diagnostic safety copy remains visible on dashboard, case detail, and
  readiness review.
- The remaining beta polish backlog is documented rather than hidden.
