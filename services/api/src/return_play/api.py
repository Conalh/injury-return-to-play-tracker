import os
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Query, Response, status

from return_play.auth import (
    RequestContext,
    authenticate_local_login,
    create_auth_token,
    get_request_context,
    require_permission,
)
from return_play.db import create_session_factory
from return_play.models import (
    ApplyTemplateRequest,
    AuthLoginRequest,
    AthleteCreate,
    ClearanceDecisionCreate,
    ClinicianNoteCreate,
    FunctionalTestCreate,
    InjuryCaseCreate,
    MilestoneResultUpdate,
    OrganizationCreate,
    ReturnPlanTemplateWithPhasesCreate,
    ShareTokenCreate,
    ShareTokenRevoke,
    SymptomLogCreate,
    UserCreate,
    UserDeactivateRequest,
    UserRoleUpdate,
    WorkloadSessionCreate,
)
from return_play.permissions import Permission
from return_play.repositories import InMemoryWorkflowRepository, SqlAlchemyWorkflowRepository


AuthenticatedContext = Annotated[RequestContext, Depends(get_request_context)]
ReadAthletesContext = Annotated[
    RequestContext, Depends(require_permission(Permission.READ_ATHLETES))
]
ManageAthletesContext = Annotated[
    RequestContext, Depends(require_permission(Permission.MANAGE_ATHLETES))
]
ReadClinicalCasesContext = Annotated[
    RequestContext, Depends(require_permission(Permission.READ_CLINICAL_CASES))
]
ManageClinicalCasesContext = Annotated[
    RequestContext, Depends(require_permission(Permission.MANAGE_CLINICAL_CASES))
]
ReadTemplatesContext = Annotated[
    RequestContext, Depends(require_permission(Permission.READ_TEMPLATES))
]
ManageTemplatesContext = Annotated[
    RequestContext, Depends(require_permission(Permission.MANAGE_TEMPLATES))
]
ReadEvidenceContext = Annotated[
    RequestContext, Depends(require_permission(Permission.READ_EVIDENCE))
]
ManageEvidenceContext = Annotated[
    RequestContext, Depends(require_permission(Permission.MANAGE_EVIDENCE))
]
ReadReadinessContext = Annotated[
    RequestContext, Depends(require_permission(Permission.READ_READINESS))
]
RecordClearanceContext = Annotated[
    RequestContext, Depends(require_permission(Permission.RECORD_CLEARANCE_DECISIONS))
]
ManageSharesContext = Annotated[
    RequestContext, Depends(require_permission(Permission.MANAGE_SHARES))
]
GenerateReportsContext = Annotated[
    RequestContext, Depends(require_permission(Permission.GENERATE_REPORTS))
]
ReadAuditLogContext = Annotated[
    RequestContext, Depends(require_permission(Permission.READ_AUDIT_LOG))
]
SeedDemoContext = Annotated[
    RequestContext, Depends(require_permission(Permission.SEED_DEMO))
]
ManageOrganizationContext = Annotated[
    RequestContext, Depends(require_permission(Permission.MANAGE_ORGANIZATION))
]
ManageUsersContext = Annotated[
    RequestContext, Depends(require_permission(Permission.MANAGE_USERS))
]
ReadOrganizationAuditLogContext = Annotated[
    RequestContext, Depends(require_permission(Permission.READ_ORGANIZATION_AUDIT_LOG))
]


def create_app(repository=None) -> FastAPI:
    repository = repository or InMemoryWorkflowRepository()
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

    @api_router.post("/auth/login")
    def login(payload: AuthLoginRequest) -> dict[str, str]:
        context = authenticate_local_login(payload.email, payload.password)
        return {
            "access_token": create_auth_token(context),
            "token_type": "bearer",
        }

    @api_router.post("/auth/logout")
    def logout(_context: AuthenticatedContext) -> dict[str, str]:
        return {"status": "logged_out"}

    @api_router.get("/me")
    def current_user(context: AuthenticatedContext) -> dict[str, str]:
        return {
            "actor_id": context.actor_id,
            "role": context.role.value,
            "organization_id": context.organization_id,
        }

    @api_router.post("/admin/organization", status_code=status.HTTP_201_CREATED)
    def setup_organization(
        payload: OrganizationCreate,
        context: ManageOrganizationContext,
    ) -> dict:
        return repository.setup_organization(payload, context)

    @api_router.post("/admin/users/invitations", status_code=status.HTTP_201_CREATED)
    def invite_user(payload: UserCreate, context: ManageUsersContext) -> dict:
        return repository.invite_user(payload, context)

    @api_router.patch("/admin/users/{user_id}/role")
    def update_user_role(
        user_id: str,
        payload: UserRoleUpdate,
        context: ManageUsersContext,
    ) -> dict:
        return repository.update_user_role(user_id, payload, context)

    @api_router.post("/admin/users/{user_id}/deactivate")
    def deactivate_user(
        user_id: str,
        payload: UserDeactivateRequest,
        context: ManageUsersContext,
    ) -> dict:
        return repository.deactivate_user(user_id, payload, context)

    @api_router.get("/admin/audit-log")
    def get_organization_audit_log(
        context: ReadOrganizationAuditLogContext,
        organization_id: str | None = Query(default=None),
    ) -> dict[str, list[dict]]:
        return repository.get_organization_audit_log(organization_id, context)

    @api_router.get("/athletes")
    def list_athletes(
        context: ReadAthletesContext,
        organization_id: str | None = Query(default=None),
    ) -> dict[str, list[dict]]:
        return repository.list_athletes(context, organization_id)

    @api_router.post("/athletes", status_code=status.HTTP_201_CREATED)
    def create_athlete(payload: AthleteCreate, context: ManageAthletesContext) -> dict:
        return repository.create_athlete(payload, context)

    @api_router.post("/injury-cases", status_code=status.HTTP_201_CREATED)
    def create_injury_case(
        payload: InjuryCaseCreate, context: ManageClinicalCasesContext
    ) -> dict:
        return repository.create_injury_case(payload, context)

    @api_router.get("/injury-cases/{case_id}")
    def get_injury_case(case_id: str, context: ReadClinicalCasesContext) -> dict:
        return repository.get_injury_case_detail(case_id, context)

    @api_router.post("/injury-cases/{case_id}/apply-template")
    def apply_template(
        case_id: str,
        payload: ApplyTemplateRequest,
        context: ManageClinicalCasesContext,
    ) -> dict:
        return repository.apply_template(case_id, payload, context)

    @api_router.get("/injury-cases/{case_id}/phases")
    def list_case_phases(
        case_id: str, context: ReadClinicalCasesContext
    ) -> dict[str, list[dict]]:
        return repository.list_case_phases(case_id, context)

    @api_router.patch("/injury-cases/{case_id}/milestones/{milestone_id}")
    def update_milestone(
        case_id: str,
        milestone_id: str,
        payload: MilestoneResultUpdate,
        context: ManageClinicalCasesContext,
    ) -> dict:
        return repository.update_milestone(case_id, milestone_id, payload, context)

    @api_router.post(
        "/injury-cases/{case_id}/notes",
        status_code=status.HTTP_201_CREATED,
    )
    def create_note(
        case_id: str,
        payload: ClinicianNoteCreate,
        context: ManageClinicalCasesContext,
    ) -> dict:
        return repository.create_note(case_id, payload, context)

    @api_router.post(
        "/injury-cases/{case_id}/symptoms",
        status_code=status.HTTP_201_CREATED,
    )
    def create_symptom_log(
        case_id: str,
        payload: SymptomLogCreate,
        context: ManageEvidenceContext,
    ) -> dict:
        return repository.create_symptom_log(case_id, payload, context)

    @api_router.get("/injury-cases/{case_id}/symptoms")
    def list_symptom_logs(
        case_id: str, context: ReadEvidenceContext
    ) -> dict[str, list[dict]]:
        return repository.list_symptom_logs(case_id, context)

    @api_router.post(
        "/injury-cases/{case_id}/functional-tests",
        status_code=status.HTTP_201_CREATED,
    )
    def create_functional_test(
        case_id: str,
        payload: FunctionalTestCreate,
        context: ManageEvidenceContext,
    ) -> dict:
        return repository.create_functional_test(case_id, payload, context)

    @api_router.get("/injury-cases/{case_id}/functional-tests")
    def list_functional_tests(
        case_id: str,
        context: ReadEvidenceContext,
    ) -> dict[str, list[dict]]:
        return repository.list_functional_tests(case_id, context)

    @api_router.post(
        "/injury-cases/{case_id}/workload-sessions",
        status_code=status.HTTP_201_CREATED,
    )
    def create_workload_session(
        case_id: str,
        payload: WorkloadSessionCreate,
        context: ManageEvidenceContext,
    ) -> dict:
        return repository.create_workload_session(case_id, payload, context)

    @api_router.get("/injury-cases/{case_id}/workload-sessions")
    def list_workload_sessions(
        case_id: str,
        context: ReadEvidenceContext,
    ) -> dict[str, list[dict]]:
        return repository.list_workload_sessions(case_id, context)

    @api_router.get("/injury-cases/{case_id}/readiness")
    def get_readiness(case_id: str, context: ReadReadinessContext) -> dict:
        return repository.get_readiness(case_id, context)

    @api_router.post(
        "/injury-cases/{case_id}/clearance",
        status_code=status.HTTP_201_CREATED,
    )
    def create_clearance_decision(
        case_id: str,
        payload: ClearanceDecisionCreate,
        context: RecordClearanceContext,
    ) -> dict:
        return repository.create_clearance_decision(case_id, payload, context)

    @api_router.post("/injury-cases/{case_id}/share", status_code=status.HTTP_201_CREATED)
    def create_share(
        case_id: str,
        payload: ShareTokenCreate,
        context: ManageSharesContext,
    ) -> dict:
        return repository.create_share(case_id, payload, context)

    @api_router.get("/injury-cases/{case_id}/report")
    def get_report(case_id: str, context: GenerateReportsContext) -> Response:
        return Response(
            content=repository.build_report(case_id, context),
            media_type="application/pdf",
        )

    @api_router.get("/injury-cases/{case_id}/audit-log")
    def get_audit_log(
        case_id: str,
        context: ReadAuditLogContext,
    ) -> dict[str, list[dict]]:
        return repository.get_audit_log(case_id, context)

    @api_router.get("/share/{token}")
    def get_share(token: str) -> dict:
        return repository.get_share(token)

    @api_router.post("/demo/seed", status_code=status.HTTP_201_CREATED)
    def seed_demo(context: SeedDemoContext, response: Response) -> dict:
        demo = repository.seed_demo(context)
        if demo["already_seeded"]:
            response.status_code = status.HTTP_200_OK
        return demo

    @api_router.post("/share/{token}/revoke")
    def revoke_share(
        token: str,
        payload: ShareTokenRevoke,
        context: ManageSharesContext,
    ) -> dict:
        return repository.revoke_share(token, payload, context)

    @api_router.get("/templates")
    def list_templates(
        context: ReadTemplatesContext,
        organization_id: str | None = Query(default=None),
    ) -> dict[str, list[dict]]:
        return repository.list_templates(context, organization_id)

    @api_router.post("/templates", status_code=status.HTTP_201_CREATED)
    def create_template(
        payload: ReturnPlanTemplateWithPhasesCreate,
        context: ManageTemplatesContext,
    ) -> dict:
        return repository.create_template(payload, context)

    app.include_router(api_router)
    return app


def create_persistent_app(database_url: str) -> FastAPI:
    return create_app(SqlAlchemyWorkflowRepository(create_session_factory(database_url)))


def create_runtime_app() -> FastAPI:
    database_url = os.getenv("RETURN_PLAY_DATABASE_URL")
    if database_url:
        return create_persistent_app(database_url)
    return create_app()


app = create_runtime_app()
