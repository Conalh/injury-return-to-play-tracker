# Project Foundation

Status: accepted for initial build

## Purpose

Create a clear starting point for building the Injury Return-To-Play Tracker
without pretending the application already exists.

The root previously contained only `PLAN.md`. This foundation establishes the
repo shape, local configuration placeholders, documentation paths, and initial
tooling choices for the first implementation pass.

## Repository Shape

```text
apps/web/
services/api/
packages/shared/
docs/foundation/
docs/product/
```

The app folders are intentionally lightweight placeholders until the first
implementation goal scaffolds real Next.js and FastAPI projects.

## Initial Tooling Direction

- Use `node` with npm for the web app unless the project later adopts `pnpm`.
- Use Python virtual environments for the API unless the project later adopts
  `uv`.
- Use Postgres for persistent data.
- Use pytest for API tests.
- Use Playwright for browser workflow tests.
- Keep app code out of root; root is for docs, repo config, and cross-project
  coordination.

`pnpm` and `uv` were not available in the local shell during this foundation
pass, so the initial docs avoid requiring them.

## Environment Policy

- `.env.example` documents required local variables.
- Real `.env` files are ignored.
- Secrets must not be committed.
- Demo data must not contain real athlete, patient, school, clinic, or guardian
  information.

## Branch/Repo Notes

The folder was not a git repository when this work began. It was initialized on
the unborn branch `foundation-goals-0-1` so the foundation work does not start on
`main` or `master`.

## Goal 0 Exit Criteria

- Project root has a README.
- Ignore/editor/env defaults exist.
- Documentation structure exists.
- Planned app boundaries are named.
- Package-manager assumptions are explicit and reversible.
- No real protected health information is introduced.

