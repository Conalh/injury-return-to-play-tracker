from __future__ import annotations

from fastapi import HTTPException, status

from return_play.auth import RequestContext
from return_play.models import AthleteCreate, AthleteUpdate
from return_play.permissions import Permission, assert_permission


class InMemoryAthleteRepositoryMixin:
    def create_athlete(self, payload: AthleteCreate, context: RequestContext) -> dict:
        assert_permission(context, Permission.MANAGE_ATHLETES)
        self._ensure_active_user(context)
        self._ensure_payload_organization(payload.organization_id, context)
        athlete = payload.model_dump(mode="json")
        athlete["id"] = self._new_id("athlete")
        self.athletes[athlete["id"]] = athlete
        return athlete

    def list_athletes(
        self,
        context: RequestContext,
        organization_id: str | None = None,
    ) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_ATHLETES)
        self._ensure_active_user(context)
        self._ensure_requested_organization(organization_id, context)
        athletes = list(self.athletes.values())
        athletes = [
            athlete
            for athlete in athletes
            if athlete["organization_id"] == context.organization_id
        ]
        return {"items": athletes}

    def update_athlete(
        self,
        athlete_id: str,
        payload: AthleteUpdate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_ATHLETES)
        self._ensure_active_user(context)
        athlete = self.athletes.get(athlete_id)
        if athlete is None or athlete["organization_id"] != context.organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Athlete not found.",
            )
        athlete.update(payload.model_dump(mode="json", exclude_unset=True))
        return athlete
