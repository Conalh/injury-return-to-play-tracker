"""Add organization user administration fields.

Revision ID: 0005_goal_14
Revises: 0004_goal_10
Create Date: 2026-05-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005_goal_14"
down_revision: Union[str, None] = "0004_goal_10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.alter_column("users", "active", server_default=None)
    op.create_table(
        "organization_audit_log_entries",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("actor_id", sa.String(length=64)),
        sa.Column("target_user_id", sa.String(length=64)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
    )
    op.create_index(
        "ix_organization_audit_log_entries_organization_id",
        "organization_audit_log_entries",
        ["organization_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_organization_audit_log_entries_organization_id",
        table_name="organization_audit_log_entries",
    )
    op.drop_table("organization_audit_log_entries")
    op.drop_column("users", "active")
