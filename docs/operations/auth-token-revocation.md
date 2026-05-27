# Auth Token Revocation

Status: Goal 39 durable token revocation foundation.

This runbook describes bearer-token revocation behavior for the production-path
API. It narrows the previous stateless-token gap and persists revocations when
the API runs with `RETURN_PLAY_DATABASE_URL`, but it is not a substitute for a
hosted identity provider.

## Scope

Covered:

- HMAC bearer tokens issued by the local login provider.
- Token IDs on every newly issued API access token.
- Logout-driven revocation for the current authenticated bearer token.
- Rejection of revoked bearer tokens on protected API routes.
- Database-backed revocation records for persistent API deployments.
- Automatic cleanup of expired revocation entries.

Not covered:

- Hosted OIDC provider validation.
- Refresh tokens.
- User-initiated device/session management.
- Administrative global session termination.

## Token Contract

Tokens created by `create_auth_token()` include:

- `sub`: authenticated actor ID.
- `role`: authenticated role.
- `organization_id`: authenticated organization boundary.
- `exp`: token expiration timestamp.
- `jti`: unique token identifier used for revocation.

The verifier rejects tokens that are malformed, expired, signed with the wrong
secret, missing the token ID, or present in the revocation registry.

## Logout Behavior

`POST /api/auth/logout` requires a valid bearer token. When token mode is
active, the endpoint records the authenticated token ID until its expiration
time and returns:

```json
{"status":"logged_out"}
```

Any later request using that same bearer token receives:

```json
{"detail":"Bearer token has been revoked."}
```

Other valid bearer tokens for the same user remain valid until they expire or
are separately revoked.

## Operational Limits

The default local app uses an in-memory revocation registry. That is acceptable
for local demos and unit tests only.

When `RETURN_PLAY_DATABASE_URL` is configured, the persistent app stores hashed
token IDs in `auth_token_revocations`. This allows logout revocation to survive
API restarts and be shared by API workers using the same database. Expired
revocations are pruned during revoke and verification checks.

Before real hosted production, choose or confirm one of:

- Hosted identity provider session revocation.
- The built-in durable revocation store shared by all API workers through the
  production database.
- Short-lived access tokens plus refresh/session revocation owned by the
  identity provider.
- A documented compensating control accepted by security/legal reviewers.

## Verification

The API authentication tests cover:

- Anonymous token-mode requests are rejected.
- Trusted local headers do not override token identity.
- Login issues bearer tokens.
- Logout revokes the current bearer token.
- Token IDs are unique, so revoking one token does not revoke another token for
  the same actor.
- Persistent apps write revocations to `auth_token_revocations`.
- Revoked tokens remain rejected after a persistent app restart.

Run:

```powershell
cd services/api
.\.venv\Scripts\python.exe -m pytest tests/test_authentication.py
```

## Launch Gate Impact

Goal 38 resolved the local stateless-token logout gap. Goal 39 adds durable
database-backed revocation for persistent deployments. The production launch
gate should continue to block broad launch until the hosted identity
architecture is selected and verified.
