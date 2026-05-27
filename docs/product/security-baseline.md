# Security Baseline

Status: Goal 26 implementation notes

This baseline establishes the first production security controls. It is not a
complete security program, but it gives the API and repository a minimum
guardrail set before deployment work begins.

## Runtime Controls

The FastAPI app configures security middleware in `return_play.security`.

Response headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`

CORS:

- `RETURN_PLAY_CORS_ORIGINS` accepts a comma-separated allowlist.
- Local defaults allow the development web ports only.
- Unknown origins do not receive `access-control-allow-origin`.

Input size:

- `RETURN_PLAY_MAX_REQUEST_BYTES` caps request body size.
- The default is 1 MiB.
- Oversized requests return `413` before route handling.

Rate limits:

- `RETURN_PLAY_AUTH_RATE_LIMIT_PER_MINUTE` limits `/api/auth/login`.
- `RETURN_PLAY_SHARE_RATE_LIMIT_PER_MINUTE` limits token-scoped
  `/api/share/*` routes.
- The current implementation is per-process and in-memory; deployment behind
  multiple workers should replace it with shared storage.

## CI Scans

`.github/workflows/security.yml` adds two security jobs:

- Dependency scan:
  - `npm audit --audit-level=high` for the Next.js app.
  - `pip-audit --strict` for the API dependency environment.
- Secret scan:
  - `scripts/scan-secrets.ps1` checks committed files for common private key,
    GitHub token, Slack token, AWS access key, and OpenAI key patterns.

The dependency scan is intended to block high-severity dependency issues while
leaving the known moderate Next/PostCSS advisory to the normal local audit
report until a non-breaking upstream fix is available.

## Dependency Update Automation

Dependency update automation is now part of the baseline maintenance program.

`.github/dependabot.yml` enables weekly dependency update pull requests for the
managed repository surfaces:

- npm updates for `apps/web`.
- pip updates for `services/api`.
- GitHub Actions updates for `.github/workflows`.

`docs/operations/dependency-update-automation.md` defines update triage,
security update response, validation, and launch-gate evidence expectations.

## Configuration

```text
RETURN_PLAY_CORS_ORIGINS=https://app.example.com,https://staging.example.com
RETURN_PLAY_MAX_REQUEST_BYTES=1048576
RETURN_PLAY_AUTH_RATE_LIMIT_PER_MINUTE=20
RETURN_PLAY_SHARE_RATE_LIMIT_PER_MINUTE=120
```

## Remaining Work

Goal 26 does not cover hosted WAF rules, distributed rate limiting, production
secret management, or deployment platform security headers. Those belong with
CI, environment configuration, and deployment goals. Goal 42 adds dependency
update automation, but a named owner still has to review and merge updates.
