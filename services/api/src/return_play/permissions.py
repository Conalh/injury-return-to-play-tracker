from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from fastapi import HTTPException, status

from return_play.models import UserRole

if TYPE_CHECKING:
    from return_play.auth import RequestContext


class Permission(str, Enum):
    READ_ATHLETES = "read_athletes"
    MANAGE_ATHLETES = "manage_athletes"
    READ_CLINICAL_CASES = "read_clinical_cases"
    MANAGE_CLINICAL_CASES = "manage_clinical_cases"
    READ_TEMPLATES = "read_templates"
    MANAGE_TEMPLATES = "manage_templates"
    READ_EVIDENCE = "read_evidence"
    MANAGE_EVIDENCE = "manage_evidence"
    READ_READINESS = "read_readiness"
    RECORD_CLEARANCE_DECISIONS = "record_clearance_decisions"
    MANAGE_SHARES = "manage_shares"
    GENERATE_REPORTS = "generate_reports"
    READ_AUDIT_LOG = "read_audit_log"
    SEED_DEMO = "seed_demo"
    READ_SHARED_STATUS = "read_shared_status"


CLINICAL_WORKFLOW_PERMISSIONS = frozenset(
    {
        Permission.READ_ATHLETES,
        Permission.MANAGE_ATHLETES,
        Permission.READ_CLINICAL_CASES,
        Permission.MANAGE_CLINICAL_CASES,
        Permission.READ_TEMPLATES,
        Permission.MANAGE_TEMPLATES,
        Permission.READ_EVIDENCE,
        Permission.MANAGE_EVIDENCE,
        Permission.READ_READINESS,
        Permission.RECORD_CLEARANCE_DECISIONS,
        Permission.MANAGE_SHARES,
        Permission.GENERATE_REPORTS,
        Permission.READ_AUDIT_LOG,
        Permission.SEED_DEMO,
    }
)


ROLE_PERMISSIONS: dict[UserRole, frozenset[Permission]] = {
    UserRole.ADMIN: CLINICAL_WORKFLOW_PERMISSIONS | {Permission.READ_SHARED_STATUS},
    UserRole.CLINICIAN: CLINICAL_WORKFLOW_PERMISSIONS | {Permission.READ_SHARED_STATUS},
    UserRole.ATHLETIC_TRAINER: CLINICAL_WORKFLOW_PERMISSIONS
    | {Permission.READ_SHARED_STATUS},
    UserRole.COACH: frozenset({Permission.READ_SHARED_STATUS}),
    UserRole.ATHLETE: frozenset({Permission.READ_SHARED_STATUS}),
    UserRole.GUARDIAN: frozenset({Permission.READ_SHARED_STATUS}),
}


def assert_permission(context: RequestContext, permission: Permission) -> None:
    if permission not in ROLE_PERMISSIONS.get(context.role, frozenset()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission is not permitted for this action.",
        )
