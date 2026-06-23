# CI Required Checks

Status: Goal 27 CI contract

Branch protection should require the checks below before merging into the
production branch. These names match the workflow job names used by GitHub.

## Required Checks

- Backend tests
- Migration head check
- Postgres integration
- Web build
- Web Playwright
- Docker compose build
- Backup restore drill
- Dependency audit
- Secret scan

## Workflow Sources

- `.github/workflows/ci.yml` runs application tests, migration checks, frontend
  build, Playwright coverage, Docker compose image builds, restore drills, and
  dependency audits. It also applies the Alembic migrations to a real Postgres
  service and runs the Postgres-backed integration tests against it.
- `.github/workflows/security.yml` runs the standalone security baseline checks,
  including Secret scan.
- `.github/dependabot.yml` opens dependency update pull requests for web, API,
  and GitHub Actions surfaces. Required checks should run on those pull
  requests before merge.
- `docs/operations/github-actions-runtime-readiness.md` documents the GitHub
  Actions Node.js runtime opt-in and response process for platform deprecation
  annotations.

## Notes

- Web Playwright runs on Windows because the local browser harness is currently
  PowerShell-based.
- Web Playwright includes axe-based accessibility smoke coverage for the
  dashboard, case detail, template builder, and limited share route. The gate
  blocks serious and critical automated WCAG violations on those demo surfaces.
- Postgres integration runs on Linux against a `postgres` service container so
  the migration-produced schema and the production database engine are exercised
  together. The rest of the backend suite runs on SQLite, which does not enforce
  foreign keys or return timezone-aware datetimes, so engine-specific bugs only
  surface in this job.
- Dependency audit is included in CI and also remains in the security workflow
  so high-severity dependency issues are visible from both the product pipeline
  and security baseline.
- The current branch protection policy should treat these checks as required
  status checks once GitHub Actions is enabled for the repository.
- JavaScript-based GitHub Actions currently opt into the Node.js 24 action
  runtime through `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24`.
