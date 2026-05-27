# Injury Return-To-Play Tracker

Clinician- and coach-friendly return-to-play tracking for injured athletes.

This project is an evidence binder and workflow tracker. It helps clinicians,
athletic trainers, athletes, coaches, and guardians see phase progress,
symptom trends, functional test evidence, workload tolerance, and explicit
human clearance decisions.

It must not diagnose injuries, recommend treatment, clear athletes
automatically, override clinicians, hide red flags, or encourage participation
through worsening symptoms.

## Current Status

The project is in foundation/specification work.

- `PLAN.md` contains the original implementation plan.
- `docs/product/product-spec.md` contains the safety-first product spec.
- `docs/foundation/project-foundation.md` defines the initial repo and tooling
  direction.

No application code has been scaffolded yet.

## Planned Stack

- Frontend: Next.js, TypeScript, Tailwind CSS, TanStack Query.
- Backend: FastAPI, Python, Pydantic.
- Data: Postgres.
- Verification: pytest for backend, Playwright for browser workflows.
- Optional export: PDF report generation.

## Project Layout

```text
apps/
  web/                 # Planned Next.js clinician and shared-view app.
services/
  api/                 # Planned FastAPI service.
packages/
  shared/              # Planned shared contracts/types where useful.
docs/
  foundation/          # Repo, tooling, and architecture decisions.
  product/             # Product, safety, and scope specs.
```

## Safety Position

Return-to-play decisions are high-stakes clinical decisions. This software can
organize evidence and make missing information visible, but every phase advance
or full-clearance action must be attributed to a named human decision-maker.

