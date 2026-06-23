from __future__ import annotations

from copy import deepcopy

from return_play.audit import AuditEventType
from return_play.auth import RequestContext
from return_play.permissions import Permission, assert_permission
from return_play.reports import build_case_report_pdf


class InMemoryReportingRepositoryMixin:
    def build_report(self, case_id: str, context: RequestContext) -> bytes:
        assert_permission(context, Permission.GENERATE_REPORTS)
        self._ensure_active_user(context)
        injury_case = self._get_case(case_id, context.organization_id)
        athlete = self.athletes[injury_case["athlete_id"]]
        readiness = self.get_readiness(case_id, context)
        self._record_audit_event(
            case_id,
            AuditEventType.REPORT_GENERATED.value,
            context.actor_id,
            {"format": "pdf"},
        )
        self._record_audit_event(
            case_id,
            AuditEventType.SENSITIVE_EXPORT_READ.value,
            context.actor_id,
            {"export_type": "case_report", "format": "pdf"},
        )
        return build_case_report_pdf(
            {
                **self.get_injury_case_detail(case_id, context),
                "athlete_name": athlete["name"],
            },
            readiness,
            self._audit_log_copies(self.audit_log_entries.get(case_id, [])),
        )

    def get_audit_log(
        self,
        case_id: str,
        context: RequestContext,
        event_type: str | None = None,
        actor_id: str | None = None,
        limit: int | None = None,
    ) -> dict[str, list[dict]]:
        assert_permission(context, Permission.READ_AUDIT_LOG)
        self._ensure_active_user(context)
        self._get_case(case_id, context.organization_id)
        events = self.audit_log_entries.get(case_id, [])
        if event_type is not None:
            events = [event for event in events if event["event_type"] == event_type]
        if actor_id is not None:
            events = [event for event in events if event["actor_id"] == actor_id]
        if limit is not None:
            events = events[:limit]
        return {"items": self._audit_log_copies(events)}

    @staticmethod
    def _audit_log_copies(events: list[dict]) -> list[dict]:
        return [deepcopy(event) for event in events]
