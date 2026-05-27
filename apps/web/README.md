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

The UI currently uses local demo data from `lib/demo-data.ts`. It is wired to
match the backend API concepts, but it does not yet fetch from the FastAPI
service.

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
