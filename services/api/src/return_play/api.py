from fastapi import APIRouter, FastAPI, Query, status

from return_play.models import (
    ApplyTemplateRequest,
    AthleteCreate,
    ClinicianNoteCreate,
    InjuryCaseCreate,
    MilestoneResultUpdate,
    ReturnPlanTemplateWithPhasesCreate,
)
from return_play.repository import InMemoryWorkflowRepository


def create_app() -> FastAPI:
    repository = InMemoryWorkflowRepository()
    app = FastAPI(
        title="Injury Return-To-Play Tracker API",
        version="0.1.0",
        summary="Evidence tracking backend for staged return-to-play workflows.",
    )

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {
            "service": "return-play-api",
            "status": "ok",
        }

    api_router = APIRouter(prefix="/api")

    @api_router.get("/athletes")
    def list_athletes(
        organization_id: str | None = Query(default=None),
    ) -> dict[str, list[dict]]:
        return repository.list_athletes(organization_id)

    @api_router.post("/athletes", status_code=status.HTTP_201_CREATED)
    def create_athlete(payload: AthleteCreate) -> dict:
        return repository.create_athlete(payload)

    @api_router.post("/injury-cases", status_code=status.HTTP_201_CREATED)
    def create_injury_case(payload: InjuryCaseCreate) -> dict:
        return repository.create_injury_case(payload)

    @api_router.get("/injury-cases/{case_id}")
    def get_injury_case(case_id: str) -> dict:
        return repository.get_injury_case_detail(case_id)

    @api_router.post("/injury-cases/{case_id}/apply-template")
    def apply_template(case_id: str, payload: ApplyTemplateRequest) -> dict:
        return repository.apply_template(case_id, payload)

    @api_router.get("/injury-cases/{case_id}/phases")
    def list_case_phases(case_id: str) -> dict[str, list[dict]]:
        return repository.list_case_phases(case_id)

    @api_router.patch("/injury-cases/{case_id}/milestones/{milestone_id}")
    def update_milestone(
        case_id: str,
        milestone_id: str,
        payload: MilestoneResultUpdate,
    ) -> dict:
        return repository.update_milestone(case_id, milestone_id, payload)

    @api_router.post(
        "/injury-cases/{case_id}/notes",
        status_code=status.HTTP_201_CREATED,
    )
    def create_note(case_id: str, payload: ClinicianNoteCreate) -> dict:
        return repository.create_note(case_id, payload)

    @api_router.get("/templates")
    def list_templates(
        organization_id: str | None = Query(default=None),
    ) -> dict[str, list[dict]]:
        return repository.list_templates(organization_id)

    @api_router.post("/templates", status_code=status.HTTP_201_CREATED)
    def create_template(payload: ReturnPlanTemplateWithPhasesCreate) -> dict:
        return repository.create_template(payload)

    app.include_router(api_router)
    return app


app = create_app()
