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
