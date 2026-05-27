from __future__ import annotations

from enum import StrEnum


class AuditEventType(StrEnum):
    ATHLETE_SYMPTOM_CHECK_IN = "athlete_symptom_check_in"
    CLEARANCE_DECISION_RECORDED = "clearance_decision_recorded"
    CLINICIAN_NOTE_RECORDED = "clinician_note_recorded"
    FUNCTIONAL_TEST_LOGGED = "functional_test_logged"
    GUARDIAN_ACKNOWLEDGMENT_RECORDED = "guardian_acknowledgment_recorded"
    MILESTONE_EVIDENCE_RECORDED = "milestone_evidence_recorded"
    REPORT_GENERATED = "report_generated"
    SENSITIVE_EXPORT_READ = "sensitive_export_read"
    SHARE_CREATED = "share_created"
    SHARE_REVOKED = "share_revoked"
    SHARE_VIEW_READ = "share_view_read"
    SYMPTOM_LOGGED = "symptom_logged"
    WORKLOAD_SESSION_LOGGED = "workload_session_logged"


AUDIT_EVENT_TAXONOMY = tuple(event_type.value for event_type in AuditEventType)
