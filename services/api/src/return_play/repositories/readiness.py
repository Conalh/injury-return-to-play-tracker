from __future__ import annotations

from typing import Protocol

from return_play.auth import RequestContext


class ReadinessRepositoryBoundary(Protocol):
    def get_readiness(self, case_id: str, context: RequestContext) -> dict:
        ...
