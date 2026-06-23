from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select

from return_play.auth import RequestContext
from return_play.db import (
    Athlete,
    InjuryCase,
    Organization,
    OrganizationAuditLogEntry,
    ShareToken,
    User,
)
from return_play.models import (
    OrganizationCreate,
    UserCreate,
    UserDeactivateRequest,
    UserRoleUpdate,
)
from return_play.permissions import Permission, assert_permission
from return_play.repositories.demo import DemoSeedService


class SqlAlchemyAdministrationRepositoryMixin:
    def seed_demo(self, context: RequestContext) -> dict:
        assert_permission(context, Permission.SEED_DEMO)
        self._ensure_active_context(context)
        return DemoSeedService(self).seed_demo(context)

    def setup_organization(self, payload: OrganizationCreate, context: RequestContext) -> dict:
        assert_permission(context, Permission.MANAGE_ORGANIZATION)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            organization = session.get(Organization, context.organization_id)
            if organization is None:
                organization = Organization(
                    id=context.organization_id,
                    name=payload.name,
                    timezone=payload.timezone,
                    created_at=self._now(),
                )
                session.add(organization)
            else:
                organization.name = payload.name
                organization.timezone = payload.timezone
            self._ensure_user(session, context.actor_id, context)
            self._record_organization_audit_event(
                session,
                organization.id,
                "organization_configured",
                context.actor_id,
                None,
                {"name": organization.name, "timezone": organization.timezone},
            )
            session.commit()
            return self._organization_dict(organization)

    def invite_user(self, payload: UserCreate, context: RequestContext) -> dict:
        assert_permission(context, Permission.MANAGE_USERS)
        self._ensure_payload_organization(payload.organization_id, context)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._ensure_context_principal(session, context)
            user = User(
                id=self._new_id("user"),
                **payload.model_dump(mode="python"),
                active=True,
                created_at=self._now(),
            )
            session.add(user)
            self._record_organization_audit_event(
                session,
                payload.organization_id,
                "user_invited",
                context.actor_id,
                user.id,
                {"email": user.email, "role": user.role},
            )
            session.commit()
            return self._user_dict(user)

    def update_user_role(
        self,
        user_id: str,
        payload: UserRoleUpdate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_USERS)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            user = self._get_user(session, user_id, context.organization_id)
            previous_role = user.role
            user.role = payload.role.value
            self._record_organization_audit_event(
                session,
                context.organization_id,
                "user_role_updated",
                context.actor_id,
                user.id,
                {"previous_role": previous_role, "new_role": user.role},
            )
            session.commit()
            return self._user_dict(user)

    def deactivate_user(
        self,
        user_id: str,
        payload: UserDeactivateRequest,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_USERS)
        self._ensure_active_context(context)
        if payload.deactivated_by != context.actor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Deactivation actor must match request context.",
            )
        with self.session_factory() as session:
            user = self._get_user(session, user_id, context.organization_id)
            user.active = False
            self._record_organization_audit_event(
                session,
                context.organization_id,
                "user_deactivated",
                context.actor_id,
                user.id,
                {"email": user.email, "role": user.role},
            )
            session.commit()
            return self._user_dict(user)

    def get_organization_audit_log(
        self,
        organization_id: str | None,
        context: RequestContext,
    ) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_ORGANIZATION_AUDIT_LOG)
        self._ensure_requested_organization(organization_id, context)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            events = session.scalars(
                select(OrganizationAuditLogEntry).where(
                    OrganizationAuditLogEntry.organization_id == context.organization_id
                )
            ).all()
            return {"items": [self._organization_audit_dict(event) for event in events]}

    def find_demo_case(self, context: RequestContext) -> dict | None:
        with self.session_factory() as session:
            row = session.execute(
                select(InjuryCase, Athlete)
                .join(Athlete, Athlete.id == InjuryCase.athlete_id)
                .where(
                    InjuryCase.organization_id == context.organization_id,
                    InjuryCase.title == "Left ankle sprain",
                    Athlete.name == "Riley Chen",
                )
            ).first()
            if row is None:
                return None
            injury_case, _athlete = row
            return self._case_dict(injury_case)

    def demo_seed_response(
        self,
        injury_case: dict,
        context: RequestContext,
        *,
        already_seeded: bool,
    ) -> dict:
        with self.session_factory() as session:
            case = self._get_case(session, injury_case["id"], context.organization_id)
            athlete = session.get(Athlete, case.athlete_id)
            current_phase = next(
                (
                    phase
                    for phase in self._case_phases(session, case.id)
                    if self._is_active_phase(phase)
                ),
                None,
            )
            share = session.scalar(
                select(ShareToken).where(
                    ShareToken.injury_case_id == case.id,
                    ShareToken.audience == "coach",
                    ShareToken.revoked_at.is_(None),
                )
            )
            readiness = self.get_readiness(case.id, context)
            return {
                "athlete_id": athlete.id,
                "athlete_name": athlete.name,
                "injury_case_id": case.id,
                "current_phase": current_phase["name"] if current_phase else None,
                "share_token": None if share is not None else None,
                "can_auto_clear": readiness["can_auto_clear"],
                "readiness_signal_count": len(readiness["signals"]),
                "already_seeded": already_seeded,
            }
