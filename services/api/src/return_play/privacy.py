from __future__ import annotations

from collections.abc import Mapping
from typing import Any


SHARE_VIEW_ALLOWED_FIELDS = frozenset(
    {
        "audience",
        "athlete_name",
        "sport",
        "injury_title",
        "current_phase",
        "participation_status",
        "allowed_activities",
        "restricted_activities",
        "next_review_date",
        "clearance_status",
        "clinician_note",
    }
)

BLOCKED_RESTRICTED_FIELDS = frozenset(
    {
        "athlete_id",
        "date_of_birth",
        "guardian_contact",
        "organization_id",
        "clinician_owner_id",
        "summary",
        "notes",
        "symptom_logs",
        "functional_tests",
        "workload_sessions",
        "clearance_decisions",
        "phases",
        "current_phase_detail",
        "token",
        "token_hash",
    }
)

RETENTION_POLICY_HOOKS = {
    "case_records": {
        "hook": "case_retention_review",
        "default_action": "retain_until_policy_configured",
        "review_trigger": "case_closed_or_organization_policy_changed",
    },
    "share_tokens": {
        "hook": "expired_share_cleanup",
        "default_action": "expire_and_revoke",
        "review_trigger": "token_expiration_or_manual_revocation",
    },
    "audit_logs": {
        "hook": "audit_log_retention_review",
        "default_action": "retain",
        "review_trigger": "organization_retention_policy_changed",
    },
}

EXPORT_DELETE_REQUEST_PLAN = {
    "export_request": [
        "verify_requesting_organization_and_actor",
        "scope_request_to_named_athlete_or_case",
        "record_sensitive_export_read_audit_event",
        "deliver_clinician_reviewed_export_only",
    ],
    "delete_request": [
        "verify_legal_and_clinical_retention_obligations",
        "disable_or_revoke_active_share_links",
        "queue_case_retention_review_policy_hook",
        "record_organization_audit_event_for_disposition",
    ],
}

PHI_HANDLING_CHECKLIST = {
    "minimum_necessary": "Only return fields required for the audience and workflow.",
    "role_boundary": "Restricted roles use token-scoped share views, not clinical APIs.",
    "auditability": "Sensitive exports and share reads are audited.",
    "revocability": "Share links expire and can be revoked.",
    "deployment_review": "Legal, HIPAA, FTC, and BAA questions remain pre-production gates.",
}


def filter_share_view(payload: Mapping[str, Any], *, audience: str) -> dict[str, Any]:
    filtered = {
        field: payload[field] for field in SHARE_VIEW_ALLOWED_FIELDS if field in payload
    }
    filtered["data_contract"] = {
        "audience": audience,
        "included_fields": sorted(filtered.keys()),
        "excluded_fields": sorted(BLOCKED_RESTRICTED_FIELDS),
    }
    return filtered


def privacy_data_controls() -> dict[str, Any]:
    return {
        "retention_policy": RETENTION_POLICY_HOOKS,
        "export_delete_request_plan": EXPORT_DELETE_REQUEST_PLAN,
        "phi_handling_checklist": PHI_HANDLING_CHECKLIST,
    }
