"""Retarget clearance_decisions.phase_id to case_phase_statuses.

Clearance decisions are recorded against a case's applied phase
(case_phase_statuses.id), not a template phase. The baseline foreign key
pointed at return_plan_phases, so every decision insert raised a foreign-key
violation under a real database.

Revision ID: 0007_clearance_phase_fk
Revises: 0006_goal_39
Create Date: 2026-05-28
"""

from typing import Sequence, Union

from alembic import op


revision: str = "0007_clearance_phase_fk"
down_revision: Union[str, None] = "0006_goal_39"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "clearance_decisions_phase_id_fkey",
        "clearance_decisions",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "clearance_decisions_phase_id_fkey",
        "clearance_decisions",
        "case_phase_statuses",
        ["phase_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "clearance_decisions_phase_id_fkey",
        "clearance_decisions",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "clearance_decisions_phase_id_fkey",
        "clearance_decisions",
        "return_plan_phases",
        ["phase_id"],
        ["id"],
    )
