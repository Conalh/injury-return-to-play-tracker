"""Add audit log entries for Goal 7.

Revision ID: 0003_goal_7
Revises: 0002_goal_3
Create Date: 2026-05-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_goal_7"
down_revision: Union[str, None] = "0002_goal_3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_log_entries",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("injury_case_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("actor_id", sa.String(length=64)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["injury_case_id"], ["injury_cases.id"]),
    )
    op.create_index(
        "ix_audit_log_entries_injury_case_id",
        "audit_log_entries",
        ["injury_case_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_audit_log_entries_injury_case_id", table_name="audit_log_entries")
    op.drop_table("audit_log_entries")
