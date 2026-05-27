from datetime import date
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
