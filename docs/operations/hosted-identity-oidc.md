# Hosted Identity OIDC

Status: Goal 40 OIDC identity-provider adapter.

The API can validate RS256 OIDC bearer tokens when token auth is enabled and
`RETURN_PLAY_AUTH_PROVIDER=oidc`. This is the provider adapter and configuration
contract; it is not proof that a hosted identity tenant has been deployed.

## Runtime Configuration

Required for OIDC mode:

- `RETURN_PLAY_AUTH_MODE=token`
- `RETURN_PLAY_AUTH_PROVIDER=oidc`
- `RETURN_PLAY_OIDC_ISSUER`
- `RETURN_PLAY_OIDC_AUDIENCE`
- `RETURN_PLAY_OIDC_JWKS_URL` for hosted providers, or
  `RETURN_PLAY_OIDC_JWKS_JSON` for local verification tests.

Claim mapping defaults:

- `RETURN_PLAY_OIDC_ROLE_CLAIM=return_play_role`
- `RETURN_PLAY_OIDC_ORGANIZATION_CLAIM=return_play_organization_id`

Production startup rejects OIDC mode unless issuer, audience, and JWKS source
are configured.

## Token Contract

Accepted OIDC access tokens must:

- Use `RS256`.
- Match the configured issuer.
- Match the configured audience.
- Include `sub`.
- Include `exp`.
- Include `jti` for local logout denylisting.
- Include a role claim that maps to a known return-play role.
- Include an organization claim that maps to the tenant boundary.

Rejected tokens return `OIDC bearer token is invalid.`

## Revocation Boundary

The app can locally revoke a current OIDC bearer token by storing its `jti` in
the auth-token revocation store. For persistent deployments, that revocation is
database-backed through `auth_token_revocations`.

This does not revoke the upstream identity-provider session. Hosted production
still needs the provider-side session, refresh-token, password reset, MFA, and
account lifecycle policy to be selected and tested.

## Verification

Covered by tests:

- Settings parse OIDC provider configuration.
- Production startup requires issuer, audience, and JWKS source in OIDC mode.
- The verifier accepts a valid RS256 token with expected issuer, audience,
  role, organization, and token ID claims.
- The verifier rejects a token with the wrong audience.
- `.env.example` documents the OIDC variables.

Run:

```powershell
cd services/api
.\.venv\Scripts\python.exe -m pytest tests/test_environment_config.py tests/test_authentication.py
```

## Launch Gate Impact

Goal 40 removes the code-level blocker for hosted OIDC validation. Broad launch
remains blocked until a real identity provider tenant is configured, tested
against the deployed environment, reviewed for legal/security posture, and
included in the support and incident runbooks. Use
`docs/operations/identity-provider-tenant-rollout.md` as the rollout evidence
package for that work.
