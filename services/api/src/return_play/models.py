from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRole(str, Enum):
    CLINICIAN = "clinician"
    ATHLETIC_TRAINER = "athletic_trainer"
    COACH = "coach"
    ATHLETE = "athlete"
    GUARDIAN = "guardian"
    ADMIN = "admin"


class InjuryCaseStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CLEARED = "cleared"
    CLOSED = "closed"


class Side(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    BILATERAL = "bilateral"
    NOT_APPLICABLE = "not_applicable"


class PhaseStatus(str, Enum):
    LOCKED = "locked"
    CURRENT = "current"
    PASSED = "passed"
    HELD = "held"


class MilestoneKind(str, Enum):
    SYMPTOM = "symptom"
    FUNCTION = "function"
    STRENGTH = "strength"
    RANGE_OF_MOTION = "range_of_motion"
    WORKLOAD = "workload"
    CLINICIAN_REVIEW = "clinician_review"
    OTHER = "other"


class MilestoneResultStatus(str, Enum):
    NOT_STARTED = "not_started"
    PASSED = "passed"
    FAILED = "failed"
    WAIVED = "waived"


class SwellingLevel(str, Enum):
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class ClearanceDecision(str, Enum):
    ADVANCE = "advance"
    HOLD = "hold"
    CLEAR_FULL = "clear_full"
    CLOSE_CASE = "close_case"


class ShareAudience(str, Enum):
    ATHLETE = "athlete"
    COACH = "coach"
    GUARDIAN = "guardian"


class ApiSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class OrganizationCreate(ApiSchema):
    name: str = Field(min_length=1)
    timezone: str = Field(default="UTC", min_length=1)


class UserCreate(ApiSchema):
    organization_id: str = Field(min_length=1)
    email: EmailStr
    name: str = Field(min_length=1)
    role: UserRole


class UserRoleUpdate(ApiSchema):
    role: UserRole


class UserDeactivateRequest(ApiSchema):
    deactivated_by: str = Field(min_length=1)


class AuthLoginRequest(ApiSchema):
    email: EmailStr
    password: str = Field(min_length=1)


class AthleteCreate(ApiSchema):
    organization_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    date_of_birth: date
    sport: str = Field(min_length=1)
    position: str | None = None
    guardian_contact: EmailStr | None = None
    active: bool = True


class AthleteUpdate(ApiSchema):
    name: str | None = Field(default=None, min_length=1)
    date_of_birth: date | None = None
    sport: str | None = Field(default=None, min_length=1)
    position: str | None = None
    guardian_contact: EmailStr | None = None
    active: bool | None = None


class InjuryCaseCreate(ApiSchema):
    organization_id: str = Field(min_length=1)
    athlete_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    injury_category: str = Field(min_length=1)
    body_region: str = Field(min_length=1)
    side: Side
    date_of_injury: date
    clinician_owner_id: str = Field(min_length=1)
    summary: str | None = None
    status: InjuryCaseStatus = InjuryCaseStatus.ACTIVE


class ReturnPlanTemplateCreate(ApiSchema):
    organization_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    injury_category: str = Field(min_length=1)
    description: str | None = None
    created_by: str = Field(min_length=1)
    version: int = Field(default=1, ge=1)
    active: bool = True


class ReturnPlanPhaseCreate(ApiSchema):
    template_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    order_index: int = Field(ge=0)
    objective: str | None = None
    minimum_days: int = Field(default=0, ge=0)
    exit_summary: str | None = None


class MilestoneCreate(ApiSchema):
    phase_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    kind: MilestoneKind
    required: bool = True
    instructions: str | None = None


class MilestoneResultCreate(ApiSchema):
    injury_case_id: str = Field(min_length=1)
    milestone_id: str = Field(min_length=1)
    status: MilestoneResultStatus = MilestoneResultStatus.NOT_STARTED
    recorded_by: str = Field(min_length=1)
    notes: str | None = None
    evidence_json: dict[str, Any] = Field(default_factory=dict)


class SymptomLogCreate(ApiSchema):
    injury_case_id: str = Field(min_length=1)
    athlete_id: str = Field(min_length=1)
    date: date
    pain: int = Field(ge=0, le=10)
    swelling: SwellingLevel
    confidence: int = Field(ge=1, le=5)
    notes: str | None = None


class AthleteSymptomCheckIn(ApiSchema):
    date: date
    pain: int = Field(ge=0, le=10)
    swelling: SwellingLevel
    confidence: int = Field(ge=1, le=5)
    notes: str | None = None


class FunctionalTestCreate(ApiSchema):
    injury_case_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    test_date: date
    result_value: float | None = None
    unit: str | None = None
    side_to_side_difference_percent: float | None = None
    passed: bool
    recorded_by: str = Field(min_length=1)
    notes: str | None = None


class WorkloadSessionCreate(ApiSchema):
    injury_case_id: str = Field(min_length=1)
    date: date
    activity: str = Field(min_length=1)
    duration_minutes: int = Field(ge=0)
    intensity: int = Field(ge=1, le=10)
    symptom_response: str | None = None
    completed: bool
    notes: str | None = None


class ClearanceDecisionCreate(ApiSchema):
    injury_case_id: str = Field(min_length=1)
    phase_id: str = Field(min_length=1)
    decision: ClearanceDecision
    decided_by: str = Field(min_length=1)
    decided_by_role: UserRole
    rationale: str = Field(min_length=1)
    restrictions: str | None = None


class ShareTokenCreate(ApiSchema):
    injury_case_id: str = Field(min_length=1)
    audience: ShareAudience
    expires_in_days: int = Field(default=7, ge=1, le=90)
    created_by: str = Field(min_length=1)
    allowed_activities: str = Field(min_length=1)
    restricted_activities: str = Field(min_length=1)
    clinician_note: str = Field(min_length=1)
    next_review_date: date | None = None


class ShareTokenRevoke(ApiSchema):
    revoked_by: str = Field(min_length=1)


class GuardianAcknowledgmentCreate(ApiSchema):
    acknowledged_by: str = Field(min_length=1)
    relationship: str = Field(min_length=1)
    message: str | None = None


class TemplateMilestoneCreate(ApiSchema):
    title: str = Field(min_length=1)
    kind: MilestoneKind
    required: bool = True
    instructions: str | None = None


class TemplatePhaseCreate(ApiSchema):
    name: str = Field(min_length=1)
    order_index: int = Field(ge=0)
    objective: str | None = None
    minimum_days: int = Field(default=0, ge=0)
    exit_summary: str | None = None
    milestones: list[TemplateMilestoneCreate] = Field(default_factory=list)


class ReturnPlanTemplateWithPhasesCreate(ReturnPlanTemplateCreate):
    phases: list[TemplatePhaseCreate] = Field(default_factory=list)


class ApplyTemplateRequest(ApiSchema):
    template_id: str = Field(min_length=1)


class MilestoneResultUpdate(ApiSchema):
    status: MilestoneResultStatus
    recorded_by: str = Field(min_length=1)
    notes: str | None = None
    evidence_json: dict[str, Any] = Field(default_factory=dict)


class ClinicianNoteCreate(ApiSchema):
    author_id: str = Field(min_length=1)
    body: str = Field(min_length=1)


class SystemStatusResponse(ApiSchema):
    service: str
    status: str


class MetricsSnapshotResponse(ApiSchema):
    service: str
    uptime_seconds: int
    requests_total: int
    errors_total: int
    responses_by_status: dict[str, int]
    requests_by_method: dict[str, int]


class LoginTokenResponse(ApiSchema):
    access_token: str
    token_type: str


class StatusResponse(ApiSchema):
    status: str


class CurrentUserResponse(ApiSchema):
    actor_id: str
    role: UserRole
    organization_id: str


class PrivacyDataControlsResponse(ApiSchema):
    retention_policy: dict[str, Any]
    export_delete_request_plan: dict[str, list[str]]
    phi_handling_checklist: dict[str, str]


class OrganizationResponse(ApiSchema):
    id: str
    name: str
    timezone: str


class UserResponse(ApiSchema):
    id: str
    organization_id: str
    email: EmailStr
    name: str
    role: UserRole
    active: bool


class OrganizationAuditEventResponse(ApiSchema):
    id: str
    organization_id: str
    event_type: str
    actor_id: str | None
    target_user_id: str | None
    created_at: datetime
    metadata_json: dict[str, Any]


class OrganizationAuditLogResponse(ApiSchema):
    items: list[OrganizationAuditEventResponse]


class AthleteResponse(ApiSchema):
    id: str
    organization_id: str
    name: str
    date_of_birth: date
    sport: str
    position: str | None = None
    guardian_contact: EmailStr | None = None
    active: bool


class AthleteListResponse(ApiSchema):
    items: list[AthleteResponse]


class InjuryCaseResponse(ApiSchema):
    id: str
    organization_id: str
    athlete_id: str
    title: str
    injury_category: str
    body_region: str
    side: Side
    date_of_injury: date
    status: InjuryCaseStatus
    clinician_owner_id: str
    summary: str | None = None
    created_at: datetime
    updated_at: datetime


class InjuryCaseListResponse(ApiSchema):
    items: list[InjuryCaseResponse]


class CaseMilestoneResponse(ApiSchema):
    id: str
    template_milestone_id: str | None = None
    title: str | None = None
    kind: MilestoneKind | None = None
    required: bool | None = None
    instructions: str | None = None
    status: MilestoneResultStatus
    recorded_by: str | None = None
    recorded_at: datetime | None = None
    notes: str | None = None
    evidence_json: dict[str, Any] = Field(default_factory=dict)


class MilestoneResultResponse(ApiSchema):
    id: str
    injury_case_id: str | None = None
    milestone_id: str | None = None
    template_milestone_id: str | None = None
    title: str | None = None
    kind: MilestoneKind | None = None
    required: bool | None = None
    instructions: str | None = None
    status: MilestoneResultStatus
    recorded_by: str | None = None
    recorded_at: datetime | None = None
    notes: str | None = None
    evidence_json: dict[str, Any] = Field(default_factory=dict)


class CasePhaseResponse(ApiSchema):
    id: str
    template_phase_id: str
    name: str
    order_index: int
    objective: str | None = None
    minimum_days: int
    exit_summary: str | None = None
    status: PhaseStatus
    clinician_note: str | None = None
    milestones: list[CaseMilestoneResponse]


class CasePhaseListResponse(ApiSchema):
    items: list[CasePhaseResponse]


class AppliedTemplateResponse(ApiSchema):
    injury_case_id: str
    template_id: str
    phases: list[CasePhaseResponse]


class ClinicianNoteResponse(ApiSchema):
    id: str
    injury_case_id: str
    author_id: str
    body: str
    created_at: datetime


class SymptomLogResponse(ApiSchema):
    id: str
    injury_case_id: str
    athlete_id: str
    date: date
    pain: int
    swelling: SwellingLevel
    confidence: int
    notes: str | None = None
    recorded_at: datetime | None = None


class SymptomLogListResponse(ApiSchema):
    items: list[SymptomLogResponse]


class FunctionalTestResponse(ApiSchema):
    id: str
    injury_case_id: str
    name: str
    test_date: date
    result_value: float | None = None
    unit: str | None = None
    side_to_side_difference_percent: float | None = None
    passed: bool
    recorded_by: str
    notes: str | None = None
    recorded_at: datetime | None = None


class FunctionalTestListResponse(ApiSchema):
    items: list[FunctionalTestResponse]


class WorkloadSessionResponse(ApiSchema):
    id: str
    injury_case_id: str
    date: date
    activity: str
    duration_minutes: int
    intensity: int
    symptom_response: str | None = None
    completed: bool
    notes: str | None = None
    recorded_at: datetime | None = None


class WorkloadSessionListResponse(ApiSchema):
    items: list[WorkloadSessionResponse]


class ClearanceDecisionResponse(ApiSchema):
    id: str
    injury_case_id: str
    phase_id: str
    decision: ClearanceDecision
    decided_by: str
    decided_by_role: UserRole
    decided_at: datetime
    rationale: str
    restrictions: str | None = None


class InjuryCaseDetailResponse(InjuryCaseResponse):
    phases: list[CasePhaseResponse]
    current_phase: CasePhaseResponse | None = None
    notes: list[ClinicianNoteResponse]
    symptom_logs: list[SymptomLogResponse]
    functional_tests: list[FunctionalTestResponse]
    workload_sessions: list[WorkloadSessionResponse]
    clearance_decisions: list[ClearanceDecisionResponse]


class ReadinessSummaryResponse(ApiSchema):
    missing_required_milestone_count: int
    concern_count: int
    missing_clearance_count: int


class ReadinessSignalResponse(ApiSchema):
    type: str
    severity: str
    message: str
    source_facts: list[dict[str, Any]]


class ReadinessResponse(ApiSchema):
    injury_case_id: str
    current_phase_id: str | None
    current_phase_name: str | None
    can_auto_clear: bool
    summary: ReadinessSummaryResponse
    signals: list[ReadinessSignalResponse]


class ShareTokenResponse(ApiSchema):
    id: str
    injury_case_id: str
    audience: ShareAudience
    expires_in_days: int | None = None
    created_by: str | None = None
    token: str | None = None
    token_hash: str
    created_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None
    allowed_activities: str
    restricted_activities: str
    clinician_note: str
    next_review_date: date | None = None


class ShareTokenCreateResponse(ShareTokenResponse):
    token: str


class ShareViewDataContractResponse(ApiSchema):
    audience: str
    included_fields: list[str]
    excluded_fields: list[str]


class ShareViewResponse(ApiSchema):
    audience: ShareAudience
    athlete_name: str
    sport: str
    injury_title: str
    current_phase: str | None = None
    participation_status: str
    allowed_activities: str
    restricted_activities: str
    next_review_date: date | None = None
    clearance_status: str
    clinician_note: str
    data_contract: ShareViewDataContractResponse


class GuardianAcknowledgmentResponse(ApiSchema):
    id: str
    share_id: str
    injury_case_id: str
    acknowledged_by: str
    relationship: str
    message: str | None = None
    created_at: datetime


class AuditEventResponse(ApiSchema):
    id: str
    injury_case_id: str
    event_type: str
    actor_id: str | None
    created_at: datetime
    metadata_json: dict[str, Any]


class AuditLogResponse(ApiSchema):
    items: list[AuditEventResponse]


class DemoSeedResponse(ApiSchema):
    athlete_id: str
    athlete_name: str
    injury_case_id: str
    current_phase: str | None = None
    share_token: str | None = None
    can_auto_clear: bool
    readiness_signal_count: int
    already_seeded: bool


class TemplateMilestoneResponse(ApiSchema):
    id: str
    phase_id: str
    title: str
    kind: MilestoneKind
    required: bool
    instructions: str | None = None


class TemplatePhaseResponse(ApiSchema):
    id: str
    template_id: str
    name: str
    order_index: int
    objective: str | None = None
    minimum_days: int
    exit_summary: str | None = None
    milestones: list[TemplateMilestoneResponse] = Field(default_factory=list)


class TemplateResponse(ApiSchema):
    id: str
    organization_id: str
    name: str
    injury_category: str
    description: str | None = None
    created_by: str
    version: int
    active: bool
    phases: list[TemplatePhaseResponse] = Field(default_factory=list)


class TemplateListResponse(ApiSchema):
    items: list[TemplateResponse]
