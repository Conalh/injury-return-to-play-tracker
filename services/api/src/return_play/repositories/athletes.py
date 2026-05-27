from __future__ import annotations

from typing import Any, Protocol

from return_play.auth import RequestContext
from return_play.models import AthleteCreate


class AthleteRepositoryBoundary(Protocol):
    def create_athlete(self, payload: AthleteCreate, context: RequestContext) -> dict:
        ...

    def list_athletes(
        self,
        context: RequestContext,
        organization_id: str | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        ...
