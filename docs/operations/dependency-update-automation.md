# Dependency Update Automation

Status: Goal 42 production-hardening package

This runbook turns dependency update automation into a managed operational
control. It does not approve dependency changes automatically; every update
still has to pass the required checks and be reviewed before merge.

## Scope

Automated update coverage applies to:

- Web dependencies in `apps/web/package.json` and `apps/web/package-lock.json`.
- API dependencies declared in `services/api/pyproject.toml`.
- GitHub Actions used by `.github/workflows`.

Out of scope:

- Runtime platform images outside this repository.
- Hosted identity provider configuration.
- Production deployment platform packages or add-ons.
- Legal or clinical content updates.

## Dependabot Configuration

`.github/dependabot.yml` defines weekly update checks for the managed surfaces:

| Surface | Ecosystem | Directory | Cadence |
| --- | --- | --- | --- |
| Web app | npm | `/apps/web` | Weekly Monday |
| API service | pip | `/services/api` | Weekly Tuesday |
| CI workflows | github-actions | `/` | Weekly Wednesday |

The configuration groups minor and patch updates per surface to reduce review
noise while keeping security updates explicitly labeled as dependency work.
Major updates are intentionally left as individual pull requests because they
need human review for breaking changes.

## Update Triage

For every automated dependency pull request:

- Confirm the changed surface: web, API, or GitHub Actions.
- Review upstream release notes for breaking changes, license changes, and
  security advisories.
- Confirm the lockfile or dependency declaration matches the intended surface.
- Leave generated update commits intact unless a manual compatibility fix is
  needed.
- Do not combine dependency updates with unrelated product work.
- Merge only after the required CI and security checks pass.

## Security Update Response

For Dependabot security updates:

- Treat high or critical advisories as release-blocking until triaged.
- Run or verify `npm audit --audit-level=high` for web dependency advisories.
- Run or verify `pip-audit --strict` for API dependency advisories.
- Attach the advisory link, affected package, fixed version, and verification
  run to the release or incident notes.
- Escalate if the update cannot be applied without breaking the clinical
  workflow, auth, reporting, sharing, or audit surfaces.
- Treat GitHub Actions runtime deprecation blockers as CI maintenance work and
  cross-reference `docs/operations/github-actions-runtime-readiness.md`.

## Validation

Required validation before merging dependency update pull requests:

- Backend tests pass.
- Migration head check passes if the API surface changed.
- Next.js production build passes if the web surface changed.
- Web Playwright workflow tests pass if the web surface changed.
- Dependency audit passes.
- Secret scan passes.
- Docker compose build validation passes for updates that affect runtime images
  or package installation.

Reference checks are documented in `docs/operations/ci-required-checks.md`.

## Launch Gate Impact

Dependency update automation reduces the manual maintenance gap in
`docs/operations/production-launch-gate.md`, but it does not remove the need
for review ownership. Before broad launch, the release owner should attach:

- The latest merged dependency update pull request or a note that no updates
  were pending.
- The latest CI run that includes dependency audit evidence.
- The latest standalone security baseline run.
- The named owner responsible for triaging dependency update pull requests.
