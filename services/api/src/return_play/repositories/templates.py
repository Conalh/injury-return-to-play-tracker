from __future__ import annotations

from typing import Protocol

from return_play.auth import RequestContext
from return_play.models import ApplyTemplateRequest, ReturnPlanTemplateWithPhasesCreate


class TemplatePlanRepositoryBoundary(Protocol):
    def create_template(
        self,
        payload: ReturnPlanTemplateWithPhasesCreate,
        context: RequestContext,
    ) -> dict:
        ...

    def list_templates(
        self,
        context: RequestContext,
        organization_id: str | None = None,
    ) -> dict[str, list[dict]]:
        ...

    def apply_template(
        self,
        payload: ApplyTemplateRequest,
        context: RequestContext,
    ) -> dict:
        ...
