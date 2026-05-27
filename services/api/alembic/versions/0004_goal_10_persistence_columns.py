"""Add persistence columns for Goal 10.

Revision ID: 0004_goal_10
Revises: 0003_goal_7
Create Date: 2026-05-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_goal_10"
down_revision: Union[str, None] = "0003_goal_7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "clearance_decisions",
        sa.Column("decided_by_role", sa.String(length=64), nullable=False),
    )
    op.add_column(
        "share_tokens",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.add_column(
        "share_tokens",
        sa.Column("allowed_activities", sa.Text(), nullable=False),
    )
    op.add_column(
        "share_tokens",
        sa.Column("restricted_activities", sa.Text(), nullable=False),
    )
    op.add_column(
        "share_tokens",
        sa.Column("clinician_note", sa.Text(), nullable=False),
    )
    op.add_column(
        "share_tokens",
        sa.Column("next_review_date", sa.Date()),
    )


def downgrade() -> None:
    op.drop_column("share_tokens", "next_review_date")
    op.drop_column("share_tokens", "clinician_note")
    op.drop_column("share_tokens", "restricted_activities")
    op.drop_column("share_tokens", "allowed_activities")
    op.drop_column("share_tokens", "created_at")
    op.drop_column("clearance_decisions", "decided_by_role")
