from __future__ import annotations

from return_play.auth import RequestContext
from return_play.demo import seed_demo_workflow


class DemoSeedService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def seed_demo(self, context: RequestContext) -> dict:
        return seed_demo_workflow(self.repository, context)

    def find_demo_case(self, context: RequestContext) -> dict | None:
        return self.repository.find_demo_case(context)

    def demo_seed_response(
        self,
        injury_case: dict,
        context: RequestContext,
        *,
        already_seeded: bool,
    ) -> dict:
        return self.repository.demo_seed_response(
            injury_case,
            context,
            already_seeded=already_seeded,
        )
