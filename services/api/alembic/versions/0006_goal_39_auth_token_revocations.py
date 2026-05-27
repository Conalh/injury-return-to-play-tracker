"""Add durable auth token revocations.

Revision ID: 0006_goal_39
Revises: 0005_goal_14
Create Date: 2026-05-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0006_goal_39"
down_revision: Union[str, None] = "0005_goal_14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "auth_token_revocations",
        sa.Column("token_id_hash", sa.String(length=64), primary_key=True),
        sa.Column("actor_id", sa.String(length=64), nullable=False),
        sa.Column("organization_id", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_auth_token_revocations_actor_id",
        "auth_token_revocations",
        ["actor_id"],
    )
    op.create_index(
        "ix_auth_token_revocations_organization_id",
        "auth_token_revocations",
        ["organization_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_auth_token_revocations_organization_id",
        table_name="auth_token_revocations",
    )
    op.drop_index(
        "ix_auth_token_revocations_actor_id",
        table_name="auth_token_revocations",
    )
    op.drop_table("auth_token_revocations")
