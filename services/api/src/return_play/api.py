from fastapi import APIRouter, FastAPI, Query, Response, status

from return_play.models import (
    ApplyTemplateRequest,
    AthleteCreate,
    ClinicianNoteCreate,
    FunctionalTestCreate,
    InjuryCaseCreate,
    MilestoneResultUpdate,
    ReturnPlanTemplateWithPhasesCreate,
    ShareTokenCreate,
    ShareTokenRevoke,
    SymptomLogCreate,
    WorkloadSessionCreate,
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

    @api_router.post(
        "/injury-cases/{case_id}/symptoms",
        status_code=status.HTTP_201_CREATED,
    )
    def create_symptom_log(case_id: str, payload: SymptomLogCreate) -> dict:
        return repository.create_symptom_log(case_id, payload)

    @api_router.get("/injury-cases/{case_id}/symptoms")
    def list_symptom_logs(case_id: str) -> dict[str, list[dict]]:
        return repository.list_symptom_logs(case_id)

    @api_router.post(
        "/injury-cases/{case_id}/functional-tests",
        status_code=status.HTTP_201_CREATED,
    )
    def create_functional_test(case_id: str, payload: FunctionalTestCreate) -> dict:
        return repository.create_functional_test(case_id, payload)

    @api_router.get("/injury-cases/{case_id}/functional-tests")
    def list_functional_tests(case_id: str) -> dict[str, list[dict]]:
        return repository.list_functional_tests(case_id)

    @api_router.post(
        "/injury-cases/{case_id}/workload-sessions",
        status_code=status.HTTP_201_CREATED,
    )
    def create_workload_session(case_id: str, payload: WorkloadSessionCreate) -> dict:
        return repository.create_workload_session(case_id, payload)

    @api_router.get("/injury-cases/{case_id}/workload-sessions")
    def list_workload_sessions(case_id: str) -> dict[str, list[dict]]:
        return repository.list_workload_sessions(case_id)

    @api_router.get("/injury-cases/{case_id}/readiness")
    def get_readiness(case_id: str) -> dict:
        return repository.get_readiness(case_id)

    @api_router.post("/injury-cases/{case_id}/share", status_code=status.HTTP_201_CREATED)
    def create_share(case_id: str, payload: ShareTokenCreate) -> dict:
        return repository.create_share(case_id, payload)

    @api_router.get("/injury-cases/{case_id}/report")
    def get_report(case_id: str) -> Response:
        return Response(
            content=repository.build_report(case_id),
            media_type="application/pdf",
        )

    @api_router.get("/injury-cases/{case_id}/audit-log")
    def get_audit_log(case_id: str) -> dict[str, list[dict]]:
        return repository.get_audit_log(case_id)

    @api_router.get("/share/{token}")
    def get_share(token: str) -> dict:
        return repository.get_share(token)

    @api_router.post("/share/{token}/revoke")
    def revoke_share(token: str, payload: ShareTokenRevoke) -> dict:
        return repository.revoke_share(token, payload)

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
