# Auth Token Revocation

Status: Goal 38 token revocation foundation.

This runbook describes the local bearer-token revocation behavior for the
production-path API. It narrows the previous stateless-token gap, but it is not
a substitute for a hosted identity provider or a durable multi-instance session
store.

## Scope

Covered:

- HMAC bearer tokens issued by the local login provider.
- Token IDs on every newly issued API access token.
- Logout-driven revocation for the current authenticated bearer token.
- Rejection of revoked bearer tokens on protected API routes.
- Automatic cleanup of expired revocation entries inside the API process.

Not covered:

- Hosted OIDC provider validation.
- Cross-process or cross-region revocation persistence.
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

The revocation registry is process-local. That is acceptable for local
production-path verification and single-process demos, but it is not enough for
broad production if the API runs multiple workers or instances.

Before real hosted production, choose one of:

- Hosted identity provider session revocation.
- A durable revocation store shared by all API workers.
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

Run:

```powershell
cd services/api
.\.venv\Scripts\python.exe -m pytest tests/test_authentication.py
```

## Launch Gate Impact

Goal 38 resolves the local stateless-token logout gap. It does not complete the
hosted identity-provider decision and does not prove durable multi-instance
revocation. The production launch gate should continue to block broad launch
until the deployment identity architecture is selected and verified.
