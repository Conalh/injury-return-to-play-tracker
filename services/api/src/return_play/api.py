from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Query, Response, status

from return_play.auth import (
    RequestContext,
    InMemoryAuthTokenRevocationStore,
    SqlAlchemyAuthTokenRevocationStore,
    authenticate_local_login,
    configure_auth_token_revocation_store,
    create_auth_token,
    get_request_context,
    require_permission,
    revoke_auth_context,
)
from return_play.config import get_settings
from return_play.db import create_session_factory
from return_play.models import (
    AppliedTemplateResponse,
    ApplyTemplateRequest,
    AthleteListResponse,
    AthleteResponse,
    AthleteSymptomCheckIn,
    AuthLoginRequest,
    AthleteCreate,
    AthleteUpdate,
    AuditLogResponse,
    CasePhaseListResponse,
    ClearanceDecisionCreate,
    ClearanceDecisionResponse,
    ClinicianNoteCreate,
    ClinicianNoteResponse,
    CurrentUserResponse,
    DemoSeedResponse,
    FunctionalTestCreate,
    FunctionalTestListResponse,
    FunctionalTestResponse,
    GuardianAcknowledgmentCreate,
    GuardianAcknowledgmentResponse,
    InjuryCaseCreate,
    InjuryCaseDetailResponse,
    InjuryCaseListResponse,
    InjuryCaseResponse,
    LoginTokenResponse,
    MilestoneResultUpdate,
    MilestoneResultResponse,
    MetricsSnapshotResponse,
    OrganizationCreate,
    OrganizationAuditLogResponse,
    OrganizationResponse,
    PrivacyDataControlsResponse,
    ReadinessResponse,
    ReturnPlanTemplateWithPhasesCreate,
    ShareTokenCreate,
    ShareTokenCreateResponse,
    ShareTokenResponse,
    ShareTokenRevoke,
    ShareViewResponse,
    StatusResponse,
    SymptomLogCreate,
    SymptomLogListResponse,
    SymptomLogResponse,
    SystemStatusResponse,
    TemplateListResponse,
    TemplateResponse,
    UserCreate,
    UserDeactivateRequest,
    UserResponse,
    UserRoleUpdate,
    WorkloadSessionCreate,
    WorkloadSessionListResponse,
    WorkloadSessionResponse,
)
from return_play.observability import configure_observability
from return_play.permissions import Permission
from return_play.privacy import privacy_data_controls
from return_play.repositories import InMemoryWorkflowRepository, SqlAlchemyWorkflowRepository
from return_play.security import configure_security


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


def create_app(repository=None, auth_token_revocation_store=None) -> FastAPI:
    repository = repository or InMemoryWorkflowRepository()
    configure_auth_token_revocation_store(
        auth_token_revocation_store or InMemoryAuthTokenRevocationStore()
    )
    app = FastAPI(
        title="Injury Return-To-Play Tracker API",
        version="0.1.0",
        summary="Evidence tracking backend for staged return-to-play workflows.",
    )
    configure_security(app)
    observability = configure_observability(app)

    @app.get("/health", tags=["system"], response_model=SystemStatusResponse)
    def health() -> dict[str, str]:
        return {
            "service": "return-play-api",
            "status": "ok",
        }

    @app.get("/ready", tags=["system"], response_model=SystemStatusResponse)
    def ready() -> dict[str, str]:
        return {
            "service": "return-play-api",
            "status": "ready",
        }

    @app.get("/metrics", tags=["system"], response_model=MetricsSnapshotResponse)
    def metrics() -> dict:
        return observability.snapshot()

    api_router = APIRouter(prefix="/api")

    @api_router.post("/auth/login", response_model=LoginTokenResponse)
    def login(payload: AuthLoginRequest) -> dict[str, str]:
        context = authenticate_local_login(payload.email, payload.password)
        return {
            "access_token": create_auth_token(context),
            "token_type": "bearer",
        }

    @api_router.post("/auth/logout", response_model=StatusResponse)
    def logout(context: AuthenticatedContext) -> dict[str, str]:
        revoke_auth_context(context)
        return {"status": "logged_out"}

    @api_router.get("/me", response_model=CurrentUserResponse)
    def current_user(context: AuthenticatedContext) -> dict[str, str]:
        return {
            "actor_id": context.actor_id,
            "role": context.role.value,
            "organization_id": context.organization_id,
        }

    @api_router.get(
        "/privacy/data-controls",
        response_model=PrivacyDataControlsResponse,
    )
    def get_privacy_data_controls(_context: ReadClinicalCasesContext) -> dict:
        return privacy_data_controls()

    @api_router.post(
        "/admin/organization",
        status_code=status.HTTP_201_CREATED,
        response_model=OrganizationResponse,
    )
    def setup_organization(
        payload: OrganizationCreate,
        context: ManageOrganizationContext,
    ) -> dict:
        return repository.setup_organization(payload, context)

    @api_router.post(
        "/admin/users/invitations",
        status_code=status.HTTP_201_CREATED,
        response_model=UserResponse,
    )
    def invite_user(payload: UserCreate, context: ManageUsersContext) -> dict:
        return repository.invite_user(payload, context)

    @api_router.patch("/admin/users/{user_id}/role", response_model=UserResponse)
    def update_user_role(
        user_id: str,
        payload: UserRoleUpdate,
        context: ManageUsersContext,
    ) -> dict:
        return repository.update_user_role(user_id, payload, context)

    @api_router.post(
        "/admin/users/{user_id}/deactivate",
        response_model=UserResponse,
    )
    def deactivate_user(
        user_id: str,
        payload: UserDeactivateRequest,
        context: ManageUsersContext,
    ) -> dict:
        return repository.deactivate_user(user_id, payload, context)

    @api_router.get(
        "/admin/audit-log",
        response_model=OrganizationAuditLogResponse,
    )
    def get_organization_audit_log(
        context: ReadOrganizationAuditLogContext,
        organization_id: str | None = Query(default=None),
    ) -> dict[str, list[dict]]:
        return repository.get_organization_audit_log(organization_id, context)

    @api_router.get("/athletes", response_model=AthleteListResponse)
    def list_athletes(
        context: ReadAthletesContext,
        organization_id: str | None = Query(default=None),
    ) -> dict[str, list[dict]]:
        return repository.list_athletes(context, organization_id)

    @api_router.post(
        "/athletes",
        status_code=status.HTTP_201_CREATED,
        response_model=AthleteResponse,
    )
    def create_athlete(payload: AthleteCreate, context: ManageAthletesContext) -> dict:
        return repository.create_athlete(payload, context)

    @api_router.patch("/athletes/{athlete_id}", response_model=AthleteResponse)
    def update_athlete(
        athlete_id: str,
        payload: AthleteUpdate,
        context: ManageAthletesContext,
    ) -> dict:
        return repository.update_athlete(athlete_id, payload, context)

    @api_router.post(
        "/injury-cases",
        status_code=status.HTTP_201_CREATED,
        response_model=InjuryCaseResponse,
    )
    def create_injury_case(
        payload: InjuryCaseCreate, context: ManageClinicalCasesContext
    ) -> dict:
        return repository.create_injury_case(payload, context)

    @api_router.get("/injury-cases", response_model=InjuryCaseListResponse)
    def list_injury_cases(
        context: ReadClinicalCasesContext,
        organization_id: str | None = Query(default=None),
    ) -> dict[str, list[dict]]:
        return repository.list_injury_cases(context, organization_id)

    @api_router.get(
        "/injury-cases/{case_id}",
        response_model=InjuryCaseDetailResponse,
    )
    def get_injury_case(case_id: str, context: ReadClinicalCasesContext) -> dict:
        return repository.get_injury_case_detail(case_id, context)

    @api_router.post(
        "/injury-cases/{case_id}/apply-template",
        response_model=AppliedTemplateResponse,
    )
    def apply_template(
        case_id: str,
        payload: ApplyTemplateRequest,
        context: ManageClinicalCasesContext,
    ) -> dict:
        return repository.apply_template(case_id, payload, context)

    @api_router.get(
        "/injury-cases/{case_id}/phases",
        response_model=CasePhaseListResponse,
    )
    def list_case_phases(
        case_id: str, context: ReadClinicalCasesContext
    ) -> dict[str, list[dict]]:
        return repository.list_case_phases(case_id, context)

    @api_router.patch(
        "/injury-cases/{case_id}/milestones/{milestone_id}",
        response_model=MilestoneResultResponse,
    )
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
        response_model=ClinicianNoteResponse,
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
        response_model=SymptomLogResponse,
    )
    def create_symptom_log(
        case_id: str,
        payload: SymptomLogCreate,
        context: ManageEvidenceContext,
    ) -> dict:
        return repository.create_symptom_log(case_id, payload, context)

    @api_router.get(
        "/injury-cases/{case_id}/symptoms",
        response_model=SymptomLogListResponse,
    )
    def list_symptom_logs(
        case_id: str, context: ReadEvidenceContext
    ) -> dict[str, list[dict]]:
        return repository.list_symptom_logs(case_id, context)

    @api_router.post(
        "/injury-cases/{case_id}/functional-tests",
        status_code=status.HTTP_201_CREATED,
        response_model=FunctionalTestResponse,
    )
    def create_functional_test(
        case_id: str,
        payload: FunctionalTestCreate,
        context: ManageEvidenceContext,
    ) -> dict:
        return repository.create_functional_test(case_id, payload, context)

    @api_router.get(
        "/injury-cases/{case_id}/functional-tests",
        response_model=FunctionalTestListResponse,
    )
    def list_functional_tests(
        case_id: str,
        context: ReadEvidenceContext,
    ) -> dict[str, list[dict]]:
        return repository.list_functional_tests(case_id, context)

    @api_router.post(
        "/injury-cases/{case_id}/workload-sessions",
        status_code=status.HTTP_201_CREATED,
        response_model=WorkloadSessionResponse,
    )
    def create_workload_session(
        case_id: str,
        payload: WorkloadSessionCreate,
        context: ManageEvidenceContext,
    ) -> dict:
        return repository.create_workload_session(case_id, payload, context)

    @api_router.get(
        "/injury-cases/{case_id}/workload-sessions",
        response_model=WorkloadSessionListResponse,
    )
    def list_workload_sessions(
        case_id: str,
        context: ReadEvidenceContext,
    ) -> dict[str, list[dict]]:
        return repository.list_workload_sessions(case_id, context)

    @api_router.get(
        "/injury-cases/{case_id}/readiness",
        response_model=ReadinessResponse,
    )
    def get_readiness(case_id: str, context: ReadReadinessContext) -> dict:
        return repository.get_readiness(case_id, context)

    @api_router.post(
        "/injury-cases/{case_id}/clearance",
        status_code=status.HTTP_201_CREATED,
        response_model=ClearanceDecisionResponse,
    )
    def create_clearance_decision(
        case_id: str,
        payload: ClearanceDecisionCreate,
        context: RecordClearanceContext,
    ) -> dict:
        return repository.create_clearance_decision(case_id, payload, context)

    @api_router.post(
        "/injury-cases/{case_id}/share",
        status_code=status.HTTP_201_CREATED,
        response_model=ShareTokenCreateResponse,
    )
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

    @api_router.get(
        "/injury-cases/{case_id}/audit-log",
        response_model=AuditLogResponse,
    )
    def get_audit_log(
        case_id: str,
        context: ReadAuditLogContext,
        event_type: str | None = None,
        actor_id: str | None = None,
        limit: int | None = Query(default=None, ge=1, le=100),
    ) -> dict[str, list[dict]]:
        return repository.get_audit_log(case_id, context, event_type, actor_id, limit)

    @api_router.get("/share/{token}", response_model=ShareViewResponse)
    def get_share(token: str) -> dict:
        return repository.get_share(token)

    @api_router.post(
        "/share/{token}/symptoms",
        status_code=status.HTTP_201_CREATED,
        response_model=SymptomLogResponse,
    )
    def create_athlete_symptom_check_in(
        token: str,
        payload: AthleteSymptomCheckIn,
    ) -> dict:
        return repository.create_athlete_symptom_check_in(token, payload)

    @api_router.post(
        "/share/{token}/guardian-acknowledgment",
        status_code=status.HTTP_201_CREATED,
        response_model=GuardianAcknowledgmentResponse,
    )
    def create_guardian_acknowledgment(
        token: str,
        payload: GuardianAcknowledgmentCreate,
    ) -> dict:
        return repository.create_guardian_acknowledgment(token, payload)

    @api_router.post(
        "/demo/seed",
        status_code=status.HTTP_201_CREATED,
        response_model=DemoSeedResponse,
    )
    def seed_demo(context: SeedDemoContext, response: Response) -> dict:
        demo = repository.seed_demo(context)
        if demo["already_seeded"]:
            response.status_code = status.HTTP_200_OK
        return demo

    @api_router.post("/share/{token}/revoke", response_model=ShareTokenResponse)
    def revoke_share(
        token: str,
        payload: ShareTokenRevoke,
        context: ManageSharesContext,
    ) -> dict:
        return repository.revoke_share(token, payload, context)

    @api_router.get("/templates", response_model=TemplateListResponse)
    def list_templates(
        context: ReadTemplatesContext,
        organization_id: str | None = Query(default=None),
    ) -> dict[str, list[dict]]:
        return repository.list_templates(context, organization_id)

    @api_router.post(
        "/templates",
        status_code=status.HTTP_201_CREATED,
        response_model=TemplateResponse,
    )
    def create_template(
        payload: ReturnPlanTemplateWithPhasesCreate,
        context: ManageTemplatesContext,
    ) -> dict:
        return repository.create_template(payload, context)

    @api_router.get("/templates/{template_id}", response_model=TemplateResponse)
    def get_template(template_id: str, context: ReadTemplatesContext) -> dict:
        return repository.get_template_detail(template_id, context)

    @api_router.patch("/templates/{template_id}", response_model=TemplateResponse)
    def update_template(
        template_id: str,
        payload: ReturnPlanTemplateWithPhasesCreate,
        context: ManageTemplatesContext,
    ) -> dict:
        return repository.update_template(template_id, payload, context)

    @api_router.post(
        "/templates/{template_id}/archive",
        response_model=TemplateResponse,
    )
    def archive_template(template_id: str, context: ManageTemplatesContext) -> dict:
        return repository.archive_template(template_id, context)

    app.include_router(api_router)
    return app


def create_persistent_app(database_url: str) -> FastAPI:
    session_factory = create_session_factory(database_url)
    return create_app(
        SqlAlchemyWorkflowRepository(session_factory),
        SqlAlchemyAuthTokenRevocationStore(session_factory),
    )


def create_runtime_app() -> FastAPI:
    settings = get_settings()
    settings.validate_startup()
    if settings.database_url:
        return create_persistent_app(settings.database_url)
    return create_app()


app = create_runtime_app()
