from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Callable

from fastapi import Depends, Header, HTTPException, status

from return_play.models import UserRole


@dataclass(frozen=True)
class RequestContext:
    actor_id: str
    role: UserRole
    organization_id: str


def get_request_context(
    x_actor_id: Annotated[str | None, Header()] = None,
    x_actor_role: Annotated[str | None, Header()] = None,
    x_organization_id: Annotated[str | None, Header()] = None,
) -> RequestContext:
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

