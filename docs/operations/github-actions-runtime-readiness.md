# GitHub Actions Runtime Readiness

Status: Goal 43 CI maintenance package

This runbook tracks repository readiness for GitHub-hosted action runtime
changes. It was added after CI and security runs surfaced Node.js 20 action
runtime deprecation annotations on the GitHub Actions platform.

## Scope

This package covers repository-owned workflow files:

- `.github/workflows/ci.yml`
- `.github/workflows/security.yml`

It applies to JavaScript-based GitHub Actions used by those workflows,
including:

- `actions/checkout@v7`
- `actions/setup-node@v6`
- `actions/setup-python@v6`

It does not change the application runtime versions used by the project. The
web build and Playwright jobs still use Node.js 22 for the Next.js app, and the
API jobs still use Python 3.11.

## Runtime Control

Both repository workflows set:

```yaml
env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: "true"
```

This opts JavaScript actions into the newer GitHub Actions Node.js 24 runtime
before the hosted runner default changes. The goal is to expose action-runtime
compatibility issues while the checks are still controlled by normal branch and
push validation.

## Validation

Required validation after runtime-control changes:

- GitHub CI run passes.
- GitHub Security Baseline run passes.
- Backend tests, migration head check, web build, web Playwright, Docker
  compose build, backup restore drill, dependency audit, and secret scan all
  remain green.
- Any remaining annotations are reviewed and separated from application test
  failures.

Reference: `docs/operations/ci-required-checks.md`.

## Upgrade Response

When a GitHub Actions runtime annotation or failure appears:

- Identify whether the failure is from an action runtime, application runtime,
  dependency install, or project test.
- Check whether the affected action has a newer major or minor version.
- Prefer a focused workflow update rather than mixing CI runtime changes with
  product changes.
- Let `docs/operations/dependency-update-automation.md` and Dependabot surface
  routine GitHub Actions version updates, but handle platform deprecation
  blockers as CI maintenance work.
- Re-run CI and Security Baseline before merging.

## Launch Gate Impact

Production launch evidence should include a recent CI run and Security Baseline
run without untriaged GitHub Actions runtime blockers. Runtime deprecation
warnings are not application defects by themselves, but unresolved action
runtime failures block a release candidate because they can hide application,
security, or migration regressions.
