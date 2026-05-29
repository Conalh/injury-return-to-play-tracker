"use client";

import { useState } from "react";
import { Filter, History } from "lucide-react";
import type { AuditEvent } from "@/lib/api-client";

type AuditHistoryPanelProps = {
  auditEvents: AuditEvent[];
};

export function AuditHistoryPanel({ auditEvents }: AuditHistoryPanelProps) {
  const [auditEventType, setAuditEventType] = useState("all");
  const filteredAuditEvents =
    auditEventType === "all"
      ? auditEvents
      : auditEvents.filter((event) => event.eventType === auditEventType);
  const visibleAuditEvents = filteredAuditEvents.slice(-8).reverse();

  return (
    <section className="rp-detail-card" id="audit-history">
      <div className="rp-detail-card-header">
        <div>
          <h2>Audit history</h2>
          <p>Recent recorded actions on this case.</p>
        </div>
        <History aria-hidden="true" className="h-5 w-5 text-[var(--rp-accent)]" />
      </div>
      <div className="rp-audit-filter">
        <Filter aria-hidden="true" className="h-3.5 w-3.5 text-[var(--rp-accent)]" />
        <select
          aria-label="Audit event type"
          id="audit-event-type-filter"
          onChange={(event) => setAuditEventType(event.target.value)}
          value={auditEventType}
        >
          <option value="all">All events</option>
          {AUDIT_EVENT_TYPES.map((eventType) => (
            <option key={eventType} value={eventType}>
              {formatEventType(eventType)}
            </option>
          ))}
        </select>
      </div>
      {visibleAuditEvents.length > 0 ? (
        <div className="rp-readiness-list">
          {visibleAuditEvents.map((event) => (
            <div key={event.id} className="rp-readiness-item">
              <p>{event.eventType}</p>
              <span>
                {event.occurredAt} - Actor: {event.actorId}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <p className="rp-auto-clear-note">No matching audit events recorded.</p>
      )}
    </section>
  );
}

const AUDIT_EVENT_TYPES = [
  "athlete_symptom_check_in",
  "clearance_decision_recorded",
  "clinician_note_recorded",
  "functional_test_logged",
  "guardian_acknowledgment_recorded",
  "milestone_evidence_recorded",
  "report_generated",
  "sensitive_export_read",
  "share_created",
  "share_revoked",
  "share_view_read",
  "symptom_logged",
  "workload_session_logged",
];

function formatEventType(value: string): string {
  return value.replaceAll("_", " ").replace(/\b\w/g, (match) => match.toUpperCase());
}
