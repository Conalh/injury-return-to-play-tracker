from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select

from return_play.auth import RequestContext
from return_play.db import Athlete
from return_play.models import AthleteCreate, AthleteUpdate
from return_play.permissions import Permission, assert_permission


class SqlAlchemyAthleteRepositoryMixin:
    def create_athlete(self, payload: AthleteCreate, context: RequestContext) -> dict:
        assert_permission(context, Permission.MANAGE_ATHLETES)
        self._ensure_active_context(context)
        self._ensure_payload_organization(payload.organization_id, context)
        with self.session_factory() as session:
            self._ensure_context_principal(session, context)
            athlete = Athlete(
                id=self._new_id("athlete"),
                **payload.model_dump(mode="python"),
            )
            session.add(athlete)
            session.commit()
            return self._athlete_dict(athlete)

    def list_athletes(
        self,
        context: RequestContext,
        organization_id: str | None = None,
    ) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_ATHLETES)
        self._ensure_requested_organization(organization_id, context)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            athletes = session.scalars(
                select(Athlete).where(Athlete.organization_id == context.organization_id)
            ).all()
            return {"items": [self._athlete_dict(athlete) for athlete in athletes]}

    def update_athlete(
        self,
        athlete_id: str,
        payload: AthleteUpdate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_ATHLETES)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            athlete = session.get(Athlete, athlete_id)
            if athlete is None or athlete.organization_id != context.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Athlete not found.",
                )
            for field, value in payload.model_dump(
                mode="python", exclude_unset=True
            ).items():
                setattr(athlete, field, value)
            session.commit()
            return self._athlete_dict(athlete)
