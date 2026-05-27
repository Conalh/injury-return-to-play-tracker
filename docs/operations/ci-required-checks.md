# CI Required Checks

Status: Goal 27 CI contract

Branch protection should require the checks below before merging into the
production branch. These names match the workflow job names used by GitHub.

## Required Checks

- Backend tests
- Migration head check
- Web build
- Web Playwright
- Docker compose build
- Backup restore drill
- Dependency audit
- Secret scan

## Workflow Sources

- `.github/workflows/ci.yml` runs application tests, migration checks, frontend
  build, Playwright coverage, Docker compose image builds, restore drills, and
  dependency audits.
- `.github/workflows/security.yml` runs the standalone security baseline checks,
  including Secret scan.

## Notes

- Web Playwright runs on Windows because the local browser harness is currently
  PowerShell-based.
- Dependency audit is included in CI and also remains in the security workflow
  so high-severity dependency issues are visible from both the product pipeline
  and security baseline.
- The current branch protection policy should treat these checks as required
  status checks once GitHub Actions is enabled for the repository.
