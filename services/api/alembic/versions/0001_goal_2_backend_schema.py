"""Goal 2 backend schema baseline.

Revision ID: 0001_goal_2
Revises:
Create Date: 2026-05-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_goal_2"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_organization_id", "users", ["organization_id"])
    op.create_table(
        "athletes",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("sport", sa.String(length=120), nullable=False),
        sa.Column("position", sa.String(length=120)),
        sa.Column("guardian_contact", sa.String(length=320)),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
    )
    op.create_index("ix_athletes_organization_id", "athletes", ["organization_id"])
    op.create_table(
        "injury_cases",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("athlete_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("injury_category", sa.String(length=120), nullable=False),
        sa.Column("body_region", sa.String(length=120), nullable=False),
        sa.Column("side", sa.String(length=32), nullable=False),
        sa.Column("date_of_injury", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("clinician_owner_id", sa.String(length=64), nullable=False),
        sa.Column("summary", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["athlete_id"], ["athletes.id"]),
        sa.ForeignKeyConstraint(["clinician_owner_id"], ["users.id"]),
    )
    op.create_index("ix_injury_cases_organization_id", "injury_cases", ["organization_id"])
    op.create_index("ix_injury_cases_athlete_id", "injury_cases", ["athlete_id"])
    op.create_table(
        "return_plan_templates",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("injury_category", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
    )
    op.create_index(
        "ix_return_plan_templates_organization_id",
        "return_plan_templates",
        ["organization_id"],
    )
    op.create_table(
        "return_plan_phases",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("template_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("objective", sa.Text()),
        sa.Column("minimum_days", sa.Integer(), nullable=False),
        sa.Column("exit_summary", sa.Text()),
        sa.ForeignKeyConstraint(["template_id"], ["return_plan_templates.id"]),
    )
    op.create_index("ix_return_plan_phases_template_id", "return_plan_phases", ["template_id"])
    op.create_table(
        "milestones",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("phase_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("kind", sa.String(length=64), nullable=False),
        sa.Column("required", sa.Boolean(), nullable=False),
        sa.Column("instructions", sa.Text()),
        sa.ForeignKeyConstraint(["phase_id"], ["return_plan_phases.id"]),
    )
    op.create_index("ix_milestones_phase_id", "milestones", ["phase_id"])
    op.create_table(
        "case_phase_statuses",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("injury_case_id", sa.String(length=64), nullable=False),
        sa.Column("phase_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("clinician_note", sa.Text()),
        sa.ForeignKeyConstraint(["injury_case_id"], ["injury_cases.id"]),
        sa.ForeignKeyConstraint(["phase_id"], ["return_plan_phases.id"]),
    )
    op.create_index(
        "ix_case_phase_statuses_injury_case_id",
        "case_phase_statuses",
        ["injury_case_id"],
    )
    op.create_index("ix_case_phase_statuses_phase_id", "case_phase_statuses", ["phase_id"])
    op.create_table(
        "milestone_results",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("injury_case_id", sa.String(length=64), nullable=False),
        sa.Column("milestone_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("recorded_by", sa.String(length=64), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text()),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["injury_case_id"], ["injury_cases.id"]),
        sa.ForeignKeyConstraint(["milestone_id"], ["milestones.id"]),
        sa.ForeignKeyConstraint(["recorded_by"], ["users.id"]),
    )
    op.create_index("ix_milestone_results_injury_case_id", "milestone_results", ["injury_case_id"])
    op.create_index("ix_milestone_results_milestone_id", "milestone_results", ["milestone_id"])
    op.create_table(
        "symptom_logs",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("injury_case_id", sa.String(length=64), nullable=False),
        sa.Column("athlete_id", sa.String(length=64), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("pain", sa.Integer(), nullable=False),
        sa.Column("swelling", sa.String(length=32), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text()),
        sa.ForeignKeyConstraint(["injury_case_id"], ["injury_cases.id"]),
        sa.ForeignKeyConstraint(["athlete_id"], ["athletes.id"]),
    )
    op.create_index("ix_symptom_logs_injury_case_id", "symptom_logs", ["injury_case_id"])
    op.create_index("ix_symptom_logs_athlete_id", "symptom_logs", ["athlete_id"])
    op.create_table(
        "functional_tests",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("injury_case_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("test_date", sa.Date(), nullable=False),
        sa.Column("result_value", sa.Float()),
        sa.Column("unit", sa.String(length=64)),
        sa.Column("side_to_side_difference_percent", sa.Float()),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("recorded_by", sa.String(length=64), nullable=False),
        sa.Column("notes", sa.Text()),
        sa.ForeignKeyConstraint(["injury_case_id"], ["injury_cases.id"]),
        sa.ForeignKeyConstraint(["recorded_by"], ["users.id"]),
    )
    op.create_index("ix_functional_tests_injury_case_id", "functional_tests", ["injury_case_id"])
    op.create_table(
        "workload_sessions",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("injury_case_id", sa.String(length=64), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("activity", sa.String(length=255), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("intensity", sa.Integer(), nullable=False),
        sa.Column("symptom_response", sa.Text()),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text()),
        sa.ForeignKeyConstraint(["injury_case_id"], ["injury_cases.id"]),
    )
    op.create_index("ix_workload_sessions_injury_case_id", "workload_sessions", ["injury_case_id"])
    op.create_table(
        "clearance_decisions",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("injury_case_id", sa.String(length=64), nullable=False),
        sa.Column("phase_id", sa.String(length=64), nullable=False),
        sa.Column("decision", sa.String(length=32), nullable=False),
        sa.Column("decided_by", sa.String(length=64), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("restrictions", sa.Text()),
        sa.ForeignKeyConstraint(["injury_case_id"], ["injury_cases.id"]),
        sa.ForeignKeyConstraint(["phase_id"], ["return_plan_phases.id"]),
        sa.ForeignKeyConstraint(["decided_by"], ["users.id"]),
    )
    op.create_index(
        "ix_clearance_decisions_injury_case_id",
        "clearance_decisions",
        ["injury_case_id"],
    )
    op.create_index("ix_clearance_decisions_phase_id", "clearance_decisions", ["phase_id"])
    op.create_table(
        "share_tokens",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("injury_case_id", sa.String(length=64), nullable=False),
        sa.Column("audience", sa.String(length=32), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["injury_case_id"], ["injury_cases.id"]),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_share_tokens_injury_case_id", "share_tokens", ["injury_case_id"])


def downgrade() -> None:
    op.drop_index("ix_share_tokens_injury_case_id", table_name="share_tokens")
    op.drop_table("share_tokens")
    op.drop_index("ix_clearance_decisions_phase_id", table_name="clearance_decisions")
    op.drop_index("ix_clearance_decisions_injury_case_id", table_name="clearance_decisions")
    op.drop_table("clearance_decisions")
    op.drop_index("ix_workload_sessions_injury_case_id", table_name="workload_sessions")
    op.drop_table("workload_sessions")
    op.drop_index("ix_functional_tests_injury_case_id", table_name="functional_tests")
    op.drop_table("functional_tests")
    op.drop_index("ix_symptom_logs_athlete_id", table_name="symptom_logs")
    op.drop_index("ix_symptom_logs_injury_case_id", table_name="symptom_logs")
    op.drop_table("symptom_logs")
    op.drop_index("ix_milestone_results_milestone_id", table_name="milestone_results")
    op.drop_index("ix_milestone_results_injury_case_id", table_name="milestone_results")
    op.drop_table("milestone_results")
    op.drop_index("ix_case_phase_statuses_phase_id", table_name="case_phase_statuses")
    op.drop_index("ix_case_phase_statuses_injury_case_id", table_name="case_phase_statuses")
    op.drop_table("case_phase_statuses")
    op.drop_index("ix_milestones_phase_id", table_name="milestones")
    op.drop_table("milestones")
    op.drop_index("ix_return_plan_phases_template_id", table_name="return_plan_phases")
    op.drop_table("return_plan_phases")
    op.drop_index(
        "ix_return_plan_templates_organization_id",
        table_name="return_plan_templates",
    )
    op.drop_table("return_plan_templates")
    op.drop_index("ix_injury_cases_athlete_id", table_name="injury_cases")
    op.drop_index("ix_injury_cases_organization_id", table_name="injury_cases")
    op.drop_table("injury_cases")
    op.drop_index("ix_athletes_organization_id", table_name="athletes")
    op.drop_table("athletes")
    op.drop_index("ix_users_organization_id", table_name="users")
    op.drop_table("users")
    op.drop_table("organizations")
