"""Add clinician notes for Goal 3.

Revision ID: 0002_goal_3
Revises: 0001_goal_2
Create Date: 2026-05-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_goal_3"
down_revision: Union[str, None] = "0001_goal_2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clinician_notes",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("injury_case_id", sa.String(length=64), nullable=False),
        sa.Column("author_id", sa.String(length=64), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["injury_case_id"], ["injury_cases.id"]),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
    )
    op.create_index(
        "ix_clinician_notes_injury_case_id",
        "clinician_notes",
        ["injury_case_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_clinician_notes_injury_case_id", table_name="clinician_notes")
    op.drop_table("clinician_notes")
