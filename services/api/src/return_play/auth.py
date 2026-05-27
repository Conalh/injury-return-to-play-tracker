from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from typing import Annotated, Callable

from fastapi import Depends, Header, HTTPException, status

from return_play.models import UserRole


@dataclass(frozen=True)
class RequestContext:
    actor_id: str
    role: UserRole
    organization_id: str


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
    }
    header = {"alg": "HS256", "typ": "return-play-token"}
    encoded_header = _base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    encoded_payload = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = _sign(f"{encoded_header}.{encoded_payload}", signing_secret)
    return f"{encoded_header}.{encoded_payload}.{signature}"


def authenticate_local_login(email: str, password: str) -> RequestContext:
    if os.getenv("RETURN_PLAY_LOCAL_AUTH_ENABLED") != "1":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Local login provider is not enabled.",
        )

    expected_email = os.getenv("RETURN_PLAY_LOCAL_AUTH_EMAIL", "")
    expected_password = os.getenv("RETURN_PLAY_LOCAL_AUTH_PASSWORD", "")
    if not (
        hmac.compare_digest(email, expected_email)
        and hmac.compare_digest(password, expected_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    try:
        role = UserRole(os.environ["RETURN_PLAY_LOCAL_AUTH_ROLE"])
    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Local login provider is not configured.",
        ) from exc

    try:
        return RequestContext(
            actor_id=os.environ["RETURN_PLAY_LOCAL_AUTH_ACTOR_ID"],
            role=role,
            organization_id=os.environ["RETURN_PLAY_LOCAL_AUTH_ORGANIZATION_ID"],
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Local login provider is not configured.",
        ) from exc


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


def _context_from_authorization_header(authorization: str | None) -> RequestContext:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required.",
        )
    token = authorization.removeprefix("Bearer ").strip()
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
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise _invalid_token() from exc

    if expires_at <= int(time.time()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token has expired.",
        )

    return RequestContext(
        actor_id=actor_id,
        role=role,
        organization_id=organization_id,
    )


def _auth_mode() -> str:
    mode = os.getenv("RETURN_PLAY_AUTH_MODE", "dev_headers").lower()
    if mode in {"token", "bearer_token"}:
        return "token"
    if mode in {"dev", "development", "dev_headers"}:
        return "dev_headers"
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Authentication mode is not configured.",
    )


def _auth_secret() -> str:
    secret = os.getenv("RETURN_PLAY_AUTH_SECRET")
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
