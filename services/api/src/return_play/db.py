from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class IdMixin:
    id: Mapped[str] = mapped_column(String(64), primary_key=True)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Organization(IdMixin, TimestampMixin, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False)


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(64), nullable=False)


class Athlete(IdMixin, Base):
    __tablename__ = "athletes"

    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[Any] = mapped_column(Date, nullable=False)
    sport: Mapped[str] = mapped_column(String(120), nullable=False)
    position: Mapped[str | None] = mapped_column(String(120))
    guardian_contact: Mapped[str | None] = mapped_column(String(320))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class InjuryCase(IdMixin, Base):
    __tablename__ = "injury_cases"

    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    athlete_id: Mapped[str] = mapped_column(
        ForeignKey("athletes.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    injury_category: Mapped[str] = mapped_column(String(120), nullable=False)
    body_region: Mapped[str] = mapped_column(String(120), nullable=False)
    side: Mapped[str] = mapped_column(String(32), nullable=False)
    date_of_injury: Mapped[Any] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    clinician_owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ReturnPlanTemplate(IdMixin, Base):
    __tablename__ = "return_plan_templates"

    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    injury_category: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class ReturnPlanPhase(IdMixin, Base):
    __tablename__ = "return_plan_phases"

    template_id: Mapped[str] = mapped_column(
        ForeignKey("return_plan_templates.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    objective: Mapped[str | None] = mapped_column(Text)
    minimum_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    exit_summary: Mapped[str | None] = mapped_column(Text)


class Milestone(IdMixin, Base):
    __tablename__ = "milestones"

    phase_id: Mapped[str] = mapped_column(
        ForeignKey("return_plan_phases.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    kind: Mapped[str] = mapped_column(String(64), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    instructions: Mapped[str | None] = mapped_column(Text)


class CasePhaseStatus(IdMixin, Base):
    __tablename__ = "case_phase_statuses"

    injury_case_id: Mapped[str] = mapped_column(
        ForeignKey("injury_cases.id"), nullable=False, index=True
    )
    phase_id: Mapped[str] = mapped_column(
        ForeignKey("return_plan_phases.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    clinician_note: Mapped[str | None] = mapped_column(Text)


class MilestoneResult(IdMixin, Base):
    __tablename__ = "milestone_results"

    injury_case_id: Mapped[str] = mapped_column(
        ForeignKey("injury_cases.id"), nullable=False, index=True
    )
    milestone_id: Mapped[str] = mapped_column(
        ForeignKey("milestones.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    recorded_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    evidence_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class SymptomLog(IdMixin, Base):
    __tablename__ = "symptom_logs"

    injury_case_id: Mapped[str] = mapped_column(
        ForeignKey("injury_cases.id"), nullable=False, index=True
    )
    athlete_id: Mapped[str] = mapped_column(
        ForeignKey("athletes.id"), nullable=False, index=True
    )
    date: Mapped[Any] = mapped_column(Date, nullable=False)
    pain: Mapped[int] = mapped_column(Integer, nullable=False)
    swelling: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class FunctionalTest(IdMixin, Base):
    __tablename__ = "functional_tests"

    injury_case_id: Mapped[str] = mapped_column(
        ForeignKey("injury_cases.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    test_date: Mapped[Any] = mapped_column(Date, nullable=False)
    result_value: Mapped[float | None] = mapped_column()
    unit: Mapped[str | None] = mapped_column(String(64))
    side_to_side_difference_percent: Mapped[float | None] = mapped_column()
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    recorded_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class WorkloadSession(IdMixin, Base):
    __tablename__ = "workload_sessions"

    injury_case_id: Mapped[str] = mapped_column(
        ForeignKey("injury_cases.id"), nullable=False, index=True
    )
    date: Mapped[Any] = mapped_column(Date, nullable=False)
    activity: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    intensity: Mapped[int] = mapped_column(Integer, nullable=False)
    symptom_response: Mapped[str | None] = mapped_column(Text)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class ClearanceDecisionRecord(IdMixin, Base):
    __tablename__ = "clearance_decisions"

    injury_case_id: Mapped[str] = mapped_column(
        ForeignKey("injury_cases.id"), nullable=False, index=True
    )
    phase_id: Mapped[str] = mapped_column(
        ForeignKey("return_plan_phases.id"), nullable=False, index=True
    )
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    decided_by: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    restrictions: Mapped[str | None] = mapped_column(Text)


class ShareToken(IdMixin, Base):
    __tablename__ = "share_tokens"

    injury_case_id: Mapped[str] = mapped_column(
        ForeignKey("injury_cases.id"), nullable=False, index=True
    )
    audience: Mapped[str] = mapped_column(String(32), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
