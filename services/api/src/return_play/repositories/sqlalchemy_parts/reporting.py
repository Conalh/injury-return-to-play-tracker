from __future__ import annotations

from sqlalchemy import select

from return_play.audit import AuditEventType
from return_play.auth import RequestContext
from return_play.db import Athlete, AuditLogEntry
from return_play.permissions import Permission, assert_permission
from return_play.reports import build_case_report_pdf


class SqlAlchemyReportingRepositoryMixin:
    def build_report(self, case_id: str, context: RequestContext) -> bytes:
        assert_permission(context, Permission.GENERATE_REPORTS)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            injury_case = self._get_case(session, case_id, context.organization_id)
            athlete = session.get(Athlete, injury_case.athlete_id)
            readiness = self.get_readiness(case_id, context)
            self._record_audit_event(
                session,
                case_id,
                AuditEventType.REPORT_GENERATED.value,
                context.actor_id,
                {"format": "pdf"},
            )
            self._record_audit_event(
                session,
                case_id,
                AuditEventType.SENSITIVE_EXPORT_READ.value,
                context.actor_id,
                {"export_type": "case_report", "format": "pdf"},
            )
            session.flush()
            audit_events = session.scalars(
                select(AuditLogEntry).where(AuditLogEntry.injury_case_id == case_id)
            ).all()
            case_detail = self._case_detail(session, injury_case)
            audit_metadata = [self._audit_dict(event) for event in audit_events]
            session.commit()
            return build_case_report_pdf(
                {
                    **case_detail,
                    "athlete_name": athlete.name,
                },
                readiness,
                audit_metadata,
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
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._get_case(session, case_id, context.organization_id)
            query = select(AuditLogEntry).where(AuditLogEntry.injury_case_id == case_id)
            if event_type is not None:
                query = query.where(AuditLogEntry.event_type == event_type)
            if actor_id is not None:
                query = query.where(AuditLogEntry.actor_id == actor_id)
            if limit is not None:
                query = query.limit(limit)
            events = session.scalars(query).all()
            return {"items": [self._audit_dict(event) for event in events]}
