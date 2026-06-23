from __future__ import annotations

from fastapi import HTTPException, status

from return_play.auth import RequestContext
from return_play.models import (
    OrganizationCreate,
    UserCreate,
    UserDeactivateRequest,
    UserRoleUpdate,
)
from return_play.permissions import Permission, assert_permission
from return_play.repositories.demo import DemoSeedService


class InMemoryAdministrationRepositoryMixin:
    def seed_demo(self, context: RequestContext) -> dict:
        assert_permission(context, Permission.SEED_DEMO)
        self._ensure_active_user(context)
        return DemoSeedService(self).seed_demo(context)

    def setup_organization(self, payload: OrganizationCreate, context: RequestContext) -> dict:
        assert_permission(context, Permission.MANAGE_ORGANIZATION)
        self._ensure_active_user(context)
        organization = {
            "id": context.organization_id,
            **payload.model_dump(mode="json"),
        }
        self.organizations[organization["id"]] = organization
        self._record_organization_audit_event(
            organization["id"],
            "organization_configured",
            context.actor_id,
            None,
            {"name": organization["name"], "timezone": organization["timezone"]},
        )
        return organization

    def invite_user(self, payload: UserCreate, context: RequestContext) -> dict:
        assert_permission(context, Permission.MANAGE_USERS)
        self._ensure_active_user(context)
        self._ensure_payload_organization(payload.organization_id, context)
        self.organizations.setdefault(
            payload.organization_id,
            {"id": payload.organization_id, "name": payload.organization_id, "timezone": "UTC"},
        )
        user = {
            "id": self._new_id("user"),
            **payload.model_dump(mode="json"),
            "active": True,
        }
        self.users[user["id"]] = user
        self._record_organization_audit_event(
            payload.organization_id,
            "user_invited",
            context.actor_id,
            user["id"],
            {"email": user["email"], "role": user["role"]},
        )
        return user

    def update_user_role(
        self,
        user_id: str,
        payload: UserRoleUpdate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_USERS)
        self._ensure_active_user(context)
        user = self._get_user(user_id, context.organization_id)
        previous_role = user["role"]
        user["role"] = payload.role.value
        self._record_organization_audit_event(
            context.organization_id,
            "user_role_updated",
            context.actor_id,
            user_id,
            {"previous_role": previous_role, "new_role": user["role"]},
        )
        return user

    def deactivate_user(
        self,
        user_id: str,
        payload: UserDeactivateRequest,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_USERS)
        self._ensure_active_user(context)
        if payload.deactivated_by != context.actor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Deactivation actor must match request context.",
            )
        user = self._get_user(user_id, context.organization_id)
        user["active"] = False
        self._record_organization_audit_event(
            context.organization_id,
            "user_deactivated",
            context.actor_id,
            user_id,
            {"email": user["email"], "role": user["role"]},
        )
        return user

    def get_organization_audit_log(
        self,
        organization_id: str | None,
        context: RequestContext,
    ) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_ORGANIZATION_AUDIT_LOG)
        self._ensure_active_user(context)
        self._ensure_requested_organization(organization_id, context)
        return {"items": self.organization_audit_log_entries.get(context.organization_id, [])}

    def find_demo_case(self, context: RequestContext) -> dict | None:
        for injury_case in self.injury_cases.values():
            if (
                injury_case["organization_id"] == context.organization_id
                and injury_case["title"] == "Left ankle sprain"
                and self.athletes[injury_case["athlete_id"]]["name"] == "Riley Chen"
            ):
                return injury_case
        return None

    def demo_seed_response(
        self,
        injury_case: dict,
        context: RequestContext,
        *,
        already_seeded: bool,
    ) -> dict:
        athlete = self.athletes[injury_case["athlete_id"]]
        phases = self.case_plans.get(injury_case["id"], [])
        current_phase = next(
            (phase for phase in phases if self._is_active_phase(phase)),
            None,
        )
        share = next(
            (
                share_token
                for share_token in self.share_tokens.values()
                if share_token["injury_case_id"] == injury_case["id"]
                and share_token["audience"] == "coach"
                and share_token["revoked_at"] is None
            ),
            None,
        )
        readiness = self.get_readiness(injury_case["id"], context)

        return {
            "athlete_id": athlete["id"],
            "athlete_name": athlete["name"],
            "injury_case_id": injury_case["id"],
            "current_phase": current_phase["name"] if current_phase else None,
            "share_token": share["token"] if share else None,
            "can_auto_clear": readiness["can_auto_clear"],
            "readiness_signal_count": len(readiness["signals"]),
            "already_seeded": already_seeded,
        }
