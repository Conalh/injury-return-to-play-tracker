# Web App

Next.js application for clinician workflows and limited shared views.

## Current Scope

Goal 6 establishes the first clinician dashboard:

- Roster dashboard at `/`.
- Case detail page at `/cases/case_demo`.
- Phase timeline.
- Current milestone gates.
- Symptom trend.
- Functional test table.
- Workload progression.
- Readiness review.
- Clearance panel.

Goal 7 adds the first limited shared view:

- Coach status page at `/share/demo-coach-token`.
- Participation status, allowed activity, restrictions, next review, and
  clearance status.
- No symptom trend, pain details, guardian contact, or full clinical record in
  the shared route.
- Non-diagnostic clearance wording that states the page is not medical
  clearance.

Goal 15 wires the dashboard to the FastAPI backend:

- `lib/api-client.ts` fetches athletes, injury cases, case detail, readiness,
  and limited share views from the API.
- `RETURN_PLAY_DATA_MODE=demo` keeps the static local fallback.
- `RETURN_PLAY_DATA_MODE=api` uses the configured API without demo seeding.
- `RETURN_PLAY_DATA_MODE=api-demo` seeds the local demo workflow first, then
  renders backend data.
- Dashboard, case detail, and share views include loading, empty, error, and
  unauthorized states.
- Playwright starts a real FastAPI server plus Next.js through
  `scripts/dev-with-api.ps1`.

Goal 16 adds the clinician case creation path:

- `/cases/new` creates an athlete, opens an injury case, applies a selected
  return-plan template, and redirects to the new case detail.
- `/athletes/[id]/edit` updates athlete profile fields used by clinical
  workflows and shared views.
- Form submissions use server actions backed by the API client, with visible
  validation and failure states.
- Playwright covers both the happy path and required-field validation.

Goal 17 adds the template builder path:

- `/templates` lists active and archived templates.
- `/templates/new` creates staged templates with phase and milestone fields.
- `/templates/[id]/edit` saves edits as a new active version.
- Archive actions remove templates from case-creation selection without deleting
  historical versions.
- Playwright proves a created template can be applied to a new case.

Goal 18 adds case-detail evidence entry:

- Case detail includes forms for symptom logs, functional tests, workload
  sessions, and current-phase milestone evidence.
- Evidence submissions use server actions and refresh the API-backed case view.
- Readiness signals update after symptom and workload evidence is recorded.
- Playwright proves browser-entered evidence appears on the case detail page.

Goal 19 adds the human clearance decision path:

- Case detail includes a clearance decision form for hold, phase advancement,
  full clearance, and case closure.
- The rationale field is required and restrictions are recorded with the latest
  decision.
- Browser submissions use the authenticated actor as the named decision maker.
- Playwright proves hold and full-clearance decisions appear in case detail.

Goal 20 adds share management on case detail:

- Clinicians can open a create-share dialog for coach, athlete, or guardian
  audiences.
- Share forms capture allowed activities, restricted activities, expiration,
  next review, and limited-view note.
- Created links show a copy affordance and can be revoked from the same panel.
- Case audit events are shown beside the share controls.
- Playwright proves a coach share excludes clinical detail and revoked links
  render the unavailable state.

Goal 21 adds the athlete portal path:

- Athlete-audience share links render an athlete-facing portal instead of the
  coach status view.
- The portal shows current phase, assigned activities, today's instructions,
  clinician message, and non-diagnostic progress language.
- Athlete symptom check-ins post through the share token without exposing
  symptom trends, functional tests, guardian contact, or the clinician case
  detail page.
- Playwright proves the check-in flow and limited-data boundary.

Goal 22 adds the guardian portal path:

- Guardian-audience share links render a conservative guardian portal.
- The portal shows participation status, restrictions, next review, clinician
  note, and non-diagnostic limited-view language.
- Guardian acknowledgments post through the share token and redirect to an
  acknowledgment confirmation.
- Playwright proves the guardian portal excludes raw clinical evidence and
  records an acknowledgment.

Goal 23 adds report downloads:

- Case detail exposes a `Download PDF report` link.
- The Next.js route proxies report bytes from the FastAPI report endpoint using
  the server-side API client, so browser downloads do not need clinical auth
  headers.
- Playwright proves the download affordance is visible on API-backed case
  detail.

Goal 24 adds case-detail audit filtering:

- The share management panel now includes an audit event type filter.
- Audit events keep stable machine-readable values while the filter uses
  readable option labels.
- Playwright proves a report download records `sensitive_export_read` and the
  case-detail audit log can filter to that event.

Goal 29 adds the frontend environment contract:

- `lib/env.ts` parses `RETURN_PLAY_ENV`, `RETURN_PLAY_DATA_MODE`,
  `RETURN_PLAY_API_BASE_URL`, bearer token, and local request-context headers.
- Production mode rejects demo-only rendering and requires
  `RETURN_PLAY_API_BASE_URL`.

Goal 44 adds interaction polish and bounds QA:

- The clinical shell, dashboard, case actions, and share controls now have
  restrained hover, focus, and motion states.
- CSS-only tooltips explain dense controls without adding client-side state.
- Motion respects `prefers-reduced-motion`.
- Playwright covers tooltip visibility, stable hover bounds, and mobile
  overflow checks.

Goal 45 adds submit-state interaction feedback:

- Evidence, clearance, share creation, and share revocation forms use a shared
  pending submit control.
- Submit controls disable while their form action is pending to guard against
  double submissions.
- Pending labels explain the in-flight operation without changing the data
  contract or route behavior.
- Playwright covers the pending-label contract on the clinical case page.

Goal 46 adds command search:

- The topbar search opens a keyboard-friendly command dialog.
- `Ctrl+K` opens the same command dialog and `Escape` closes it.
- Commands filter across demo athlete, case, evidence, decisions, templates,
  and report destinations.
- Playwright covers dialog open, filtering, navigation, keyboard open, and
  dismissal.

Goal 47 adds the clinical notification center:

- The topbar bell opens a clinical notifications popover.
- Notifications surface symptom review, workload progression, and milestone
  evidence alerts for the demo case.
- Alert links route directly to the relevant case workflow and close the
  popover on selection.
- `Escape` dismisses the notification popover.
- Playwright covers open, alert content, routing, and dismissal.

Goal 48 adds the clinician profile and workspace menu:

- The topbar physician chip opens a clinician workspace menu.
- The menu shows signed-in clinician identity, role, organization, and demo
  environment context.
- Quick links route to workspace settings, template management, the demo case,
  and the demo report.
- `Escape` dismisses the profile menu.
- Playwright covers menu open, context content, routing, and dismissal.

Goal 49 adds sidebar workflow section routing:

- Primary sidebar links route to dashboard anchors for active cases, athlete
  roster, evidence/action queue, decision queue, and workspace settings.
- Dashboard sections expose accessible region labels and sticky-topbar-aware
  scroll targets.
- The clinician profile settings shortcut lands on the same workspace settings
  section.
- Playwright covers sidebar hashes, visible anchored regions, and profile
  settings routing.

Goal 50 adds contextual shell breadcrumbs and active navigation:

- The topbar breadcrumb reflects dashboard sections, case detail, new case, and
  template routes.
- The primary sidebar marks the current route or dashboard section with
  `aria-current`.
- Dashboard hash changes update the active sidebar item without a full reload.
- Playwright covers breadcrumb text and active nav state across dashboard,
  section anchors, case routes, and templates.

Goal 51 adds honest shell metrics:

- The primary sidebar no longer displays hardcoded count badges.
- Dashboard KPI cards remain the current source of truth for workload counts.
- Sidebar navigation keeps contextual breadcrumbs and active `aria-current`
  state from Goal 50.
- Playwright covers the absence of decorative shell count badges while
  dashboard workload metrics remain visible.

Goal 52 tightens count-free sidebar layout bounds:

- The primary sidebar no longer reserves a stale badge column after count
  badges were removed.
- Mobile sidebar navigation scrolls inside its own rail without widening the
  page.
- Long navigation labels truncate inside stable tap targets.
- Playwright covers compact navigation bounds, contained horizontal scrolling,
  and access to later sidebar links on mobile.

Goal 53 adds automated accessibility smoke coverage:

- `accessibility.spec.ts` runs axe-based WCAG checks on the dashboard, case
  detail, template builder, and limited coach share view.
- Serious and critical automated accessibility violations fail the Playwright
  suite.
- The case-detail symptom chart, functional-test table, and milestone badges
  were adjusted to satisfy the new gate without changing workflow behavior.

## Local Commands

```powershell
npm install
npm run dev
npm test
npm run build
```

The local dev server runs at:

```text
http://127.0.0.1:3217
```

API-backed local mode:

```powershell
$env:RETURN_PLAY_DATA_MODE="api-demo"
$env:RETURN_PLAY_API_BASE_URL="http://127.0.0.1:8000"
$env:RETURN_PLAY_ACTOR_ID="clinician_demo"
$env:RETURN_PLAY_ACTOR_ROLE="clinician"
$env:RETURN_PLAY_ORGANIZATION_ID="org_demo"
npm run dev
```

Production mode requires:

```powershell
$env:RETURN_PLAY_ENV="production"
$env:RETURN_PLAY_DATA_MODE="api"
$env:RETURN_PLAY_API_BASE_URL="https://api.example.com"
$env:RETURN_PLAY_API_TOKEN="<issued-bearer-token>"
npm run build
```
