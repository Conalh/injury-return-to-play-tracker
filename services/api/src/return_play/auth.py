from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from secrets import token_urlsafe
from typing import Annotated, Any, Callable, Protocol

from fastapi import Depends, Header, HTTPException, status
import jwt
from sqlalchemy import delete, select

from return_play.config import get_settings
from return_play.db import AuthTokenRevocation
from return_play.models import UserRole


@dataclass(frozen=True)
class RequestContext:
    actor_id: str
    role: UserRole
    organization_id: str
    token_id: str | None = None
    token_expires_at: int | None = None


class AuthTokenRevocationStore(Protocol):
    def revoke(self, context: RequestContext) -> None:
        ...

    def is_revoked(self, token_id: str, now: int) -> bool:
        ...


class InMemoryAuthTokenRevocationStore:
    def __init__(self) -> None:
        self._revoked_token_ids: dict[str, int] = {}

    def revoke(self, context: RequestContext) -> None:
        if context.token_id is None or context.token_expires_at is None:
            return

        self._prune(int(time.time()))
        self._revoked_token_ids[_hash_token_id(context.token_id)] = context.token_expires_at

    def is_revoked(self, token_id: str, now: int) -> bool:
        self._prune(now)
        return _hash_token_id(token_id) in self._revoked_token_ids

    def _prune(self, now: int) -> None:
        expired_token_ids = [
            token_id_hash
            for token_id_hash, expires_at in self._revoked_token_ids.items()
            if expires_at <= now
        ]
        for token_id_hash in expired_token_ids:
            del self._revoked_token_ids[token_id_hash]


class SqlAlchemyAuthTokenRevocationStore:
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def revoke(self, context: RequestContext) -> None:
        if context.token_id is None or context.token_expires_at is None:
            return

        now = int(time.time())
        revoked_at = _datetime_from_timestamp(now)
        expires_at = _datetime_from_timestamp(context.token_expires_at)
        token_id_hash = _hash_token_id(context.token_id)
        with self._session_factory() as session:
            self._prune(session, now)
            existing = session.get(AuthTokenRevocation, token_id_hash)
            if existing is None:
                session.add(
                    AuthTokenRevocation(
                        token_id_hash=token_id_hash,
                        actor_id=context.actor_id,
                        organization_id=context.organization_id,
                        expires_at=expires_at,
                        revoked_at=revoked_at,
                    )
                )
            else:
                existing.expires_at = expires_at
                existing.revoked_at = revoked_at
            session.commit()

    def is_revoked(self, token_id: str, now: int) -> bool:
        with self._session_factory() as session:
            self._prune(session, now)
            token_id_hash = _hash_token_id(token_id)
            result = session.execute(
                select(AuthTokenRevocation.token_id_hash).where(
                    AuthTokenRevocation.token_id_hash == token_id_hash
                )
            ).scalar_one_or_none()
            session.commit()
            return result is not None

    def _prune(self, session, now: int) -> None:
        session.execute(
            delete(AuthTokenRevocation).where(
                AuthTokenRevocation.expires_at <= _datetime_from_timestamp(now)
            )
        )


_auth_token_revocation_store: AuthTokenRevocationStore = InMemoryAuthTokenRevocationStore()


def configure_auth_token_revocation_store(store: AuthTokenRevocationStore) -> None:
    global _auth_token_revocation_store

    _auth_token_revocation_store = store


def create_auth_token(
    context: RequestContext,
    *,
    secret: str | None = None,
    expires_in_seconds: int = 3600,
) -> str:
    signing_secret = secret or _auth_secret()
    payload = {
        "sub": context.actor_id,
        "role": context.role.value if isinstance(context.role, UserRole) else context.role,
        "organization_id": context.organization_id,
        "exp": int(time.time()) + expires_in_seconds,
        "jti": token_urlsafe(24),
    }
    header = {"alg": "HS256", "typ": "return-play-token"}
    encoded_header = _base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    encoded_payload = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = _sign(f"{encoded_header}.{encoded_payload}", signing_secret)
    return f"{encoded_header}.{encoded_payload}.{signature}"


def authenticate_local_login(email: str, password: str) -> RequestContext:
    settings = get_settings()
    if not settings.local_auth_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Local login provider is not enabled.",
        )

    expected_email = settings.local_auth_email or ""
    expected_password = settings.local_auth_password or ""
    if not (
        hmac.compare_digest(email, expected_email)
        and hmac.compare_digest(password, expected_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    try:
        role = UserRole(settings.local_auth_role)
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Local login provider is not configured.",
        ) from exc

    if not settings.local_auth_actor_id or not settings.local_auth_organization_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Local login provider is not configured.",
        )

    return RequestContext(
        actor_id=settings.local_auth_actor_id,
        role=role,
        organization_id=settings.local_auth_organization_id,
    )


def revoke_auth_context(context: RequestContext) -> None:
    _auth_token_revocation_store.revoke(context)


def get_request_context(
    authorization: Annotated[str | None, Header()] = None,
    x_actor_id: Annotated[str | None, Header()] = None,
    x_actor_role: Annotated[str | None, Header()] = None,
    x_organization_id: Annotated[str | None, Header()] = None,
) -> RequestContext:
    if _auth_mode() == "token":
        return _context_from_authorization_header(authorization)

    if not x_actor_id or not x_actor_role or not x_organization_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated request context required.",
        )

    try:
        role = UserRole(x_actor_role)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated request context required.",
        ) from exc

    return RequestContext(
        actor_id=x_actor_id,
        role=role,
        organization_id=x_organization_id,
    )


def require_roles(*allowed_roles: UserRole) -> Callable[[RequestContext], RequestContext]:
    def dependency(
        context: Annotated[RequestContext, Depends(get_request_context)],
    ) -> RequestContext:
        if context.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role is not permitted for this action.",
            )
        return context

    return dependency


def require_permission(permission) -> Callable[[RequestContext], RequestContext]:
    def dependency(
        context: Annotated[RequestContext, Depends(get_request_context)],
    ) -> RequestContext:
        from return_play.permissions import assert_permission

        assert_permission(context, permission)
        return context

    return dependency


def _context_from_authorization_header(authorization: str | None) -> RequestContext:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required.",
        )
    token = authorization.removeprefix("Bearer ").strip()
    if get_settings().auth_provider == "oidc":
        return _verify_oidc_token(token)
    return _verify_auth_token(token, _auth_secret())


def _verify_auth_token(token: str, secret: str) -> RequestContext:
    parts = token.split(".")
    if len(parts) != 3:
        raise _invalid_token()

    encoded_header, encoded_payload, signature = parts
    expected_signature = _sign(f"{encoded_header}.{encoded_payload}", secret)
    if not hmac.compare_digest(signature, expected_signature):
        raise _invalid_token()

    try:
        payload = json.loads(_base64url_decode(encoded_payload))
        role = UserRole(payload["role"])
        actor_id = payload["sub"]
        organization_id = payload["organization_id"]
        expires_at = int(payload["exp"])
        token_id = payload["jti"]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise _invalid_token() from exc

    now = int(time.time())
    if expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token has expired.",
        )
    if _auth_token_revocation_store.is_revoked(str(token_id), now):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token has been revoked.",
        )

    return RequestContext(
        actor_id=actor_id,
        role=role,
        organization_id=organization_id,
        token_id=str(token_id),
        token_expires_at=expires_at,
    )


def _verify_oidc_token(token: str) -> RequestContext:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            _oidc_public_key(token),
            algorithms=["RS256"],
            audience=settings.oidc_audience,
            issuer=settings.oidc_issuer,
        )
        role = UserRole(payload[settings.oidc_role_claim])
        actor_id = payload["sub"]
        organization_id = payload[settings.oidc_organization_claim]
        token_id = payload["jti"]
        expires_at = int(payload["exp"])
    except (
        KeyError,
        TypeError,
        ValueError,
        jwt.InvalidTokenError,
        json.JSONDecodeError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OIDC bearer token is invalid.",
        ) from exc

    now = int(time.time())
    if _auth_token_revocation_store.is_revoked(str(token_id), now):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token has been revoked.",
        )

    return RequestContext(
        actor_id=str(actor_id),
        role=role,
        organization_id=str(organization_id),
        token_id=str(token_id),
        token_expires_at=expires_at,
    )


def _oidc_public_key(token: str) -> Any:
    settings = get_settings()
    if settings.oidc_jwks_json:
        return _oidc_public_key_from_jwks_json(token, settings.oidc_jwks_json)
    if settings.oidc_jwks_url:
        return jwt.PyJWKClient(settings.oidc_jwks_url).get_signing_key_from_jwt(token).key
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="OIDC JWKS is not configured.",
    )


def _oidc_public_key_from_jwks_json(token: str, jwks_json: str) -> Any:
    header = jwt.get_unverified_header(token)
    key_id = header.get("kid")
    jwks = json.loads(jwks_json)
    for key in jwks.get("keys", []):
        if key.get("kid") == key_id:
            return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
    raise jwt.InvalidTokenError("No matching OIDC signing key.")


def _auth_mode() -> str:
    return get_settings().auth_mode


def _auth_secret() -> str:
    secret = get_settings().auth_secret
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication secret is not configured.",
        )
    return secret


def _sign(message: str, secret: str) -> str:
    digest = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
    return _base64url_encode(digest)


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}")


def _invalid_token() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Bearer token is invalid.",
    )


def _hash_token_id(token_id: str) -> str:
    return hashlib.sha256(token_id.encode("utf-8")).hexdigest()


def _datetime_from_timestamp(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
