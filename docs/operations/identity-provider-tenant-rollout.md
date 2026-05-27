# Identity Provider Tenant Rollout

Status: Goal 41 hosted identity tenant rollout package.

This package defines the work required to turn the Goal 40 OIDC adapter into a
real hosted identity setup. It is a rollout checklist and evidence packet, not
proof that staging or production identity has been deployed.

## Scope

Covered:

- Hosted identity tenant configuration requirements.
- Account lifecycle expectations.
- MFA and password policy expectations.
- Provider-side session and refresh-token policy expectations.
- OIDC claim mapping for return-play roles and organization tenancy.
- Smoke tests required before real athlete data.
- Evidence that must be attached to the production launch gate.

Not covered:

- Creating a real provider tenant in this repository.
- Managing provider secrets or client credentials in git.
- Staging or production deployment.
- Contract, BAA, or subprocessor approval.

Reference: `docs/operations/hosted-identity-oidc.md`.

## Tenant Configuration Checklist

Before broad launch, the identity owner must configure and record:

- Provider name and tenant/environment name.
- Application/client ID for the API audience.
- API audience matching `RETURN_PLAY_OIDC_AUDIENCE`.
- Issuer matching `RETURN_PLAY_OIDC_ISSUER`.
- JWKS endpoint matching `RETURN_PLAY_OIDC_JWKS_URL`.
- Redirect/logout URLs for the deployed web app if browser login is used.
- Token signing algorithm set to RS256 or an explicitly reviewed equivalent.
- Secret/client credential storage outside the repository.
- Emergency/break-glass administrator ownership.

The deployed API must run with:

- `RETURN_PLAY_AUTH_MODE=token`
- `RETURN_PLAY_AUTH_PROVIDER=oidc`
- `RETURN_PLAY_OIDC_ISSUER`
- `RETURN_PLAY_OIDC_AUDIENCE`
- `RETURN_PLAY_OIDC_JWKS_URL`

## Account Lifecycle

The provider must support and document:

- User invitation or provisioning owner.
- Role assignment owner.
- Organization assignment owner.
- Deactivation path when a clinician, trainer, admin, coach, athlete, or
  guardian leaves the organization.
- Immediate deprovision path for suspected compromise.
- Review cadence for inactive accounts.
- Audit trail for provisioning, role changes, and deprovision events.

The app still enforces local role and organization authorization after token
validation. Provider lifecycle controls must make sure the upstream token
claims stay aligned with approved access.

## MFA And Password Policy

Minimum policy before real athlete data:

- MFA required for administrators and clinical users.
- MFA strongly preferred or risk-reviewed for limited non-clinical portal
  accounts if they become authenticated accounts.
- Password length, reuse, lockout, and reset policy reviewed by security owner.
- Recovery flow documented for lost MFA devices.
- Break-glass admin accounts documented and monitored.

## Session And Token Policy

Provider-side session policy must define:

- Access token lifetime.
- Refresh-token lifetime, rotation, and revocation behavior.
- Provider-side session termination behavior.
- Logout behavior in the web app and identity provider.
- Emergency session revocation process.
- How local API logout denylisting in `auth_token_revocations` fits with
  provider-side session revocation.

Local API logout revokes the current bearer token for the API, but it does not
terminate the upstream provider-side session by itself.

## Claims And Role Mapping

Required OIDC claims:

- `sub`: stable actor identifier.
- `jti`: token identifier used for API denylisting.
- `return_play_role`: default role claim, unless
  `RETURN_PLAY_OIDC_ROLE_CLAIM` is overridden.
- `return_play_organization_id`: default organization claim, unless
  `RETURN_PLAY_OIDC_ORGANIZATION_CLAIM` is overridden.

Allowed role values must map to the app's role matrix:

- `admin`
- `clinician`
- `athletic_trainer`
- `coach`
- `athlete`
- `guardian`

Role and organization claims must be assigned by a trusted provider-side rule,
group mapping, or custom claim process. They must not be writable by normal
users.

## Smoke Test Plan

Run these checks in the target staging or production-like environment:

- Valid admin token can call `/api/me` and receives the expected role and
  organization.
- Valid clinician token can load the roster for its own organization.
- Valid token with wrong audience is rejected.
- Valid token with wrong issuer is rejected.
- Token missing `return_play_role` is rejected.
- Token missing `return_play_organization_id` is rejected.
- Deactivated or deprovisioned provider account can no longer access the app.
- Logout revokes the current API token.
- Provider-side session revocation prevents obtaining new valid API tokens.
- Audit/logging captures enough identity metadata for incident review without
  logging full tokens or clinical payloads.

## Evidence To Attach

Attach these items to the production launch gate:

- Provider and tenant/environment name.
- OIDC issuer, audience, and JWKS URL.
- Claim mapping screenshot or exported policy summary.
- MFA/password/session policy summary.
- Account lifecycle owner and deprovision runbook link.
- Smoke test date, operator, and results.
- Security/legal reviewer signoff or accepted residual risk.
- Incident owner for identity compromise.

## Launch Gate Impact

Goal 41 turns hosted identity from a vague blocker into a concrete rollout and
evidence package. Broad launch remains blocked until a real tenant is configured
outside the repository, the smoke test plan passes in the deployed environment,
and the evidence is attached to `docs/operations/production-launch-gate.md`.
