"use client";

import { useState } from "react";
import { Copy, Filter, Link2, Share2, X } from "lucide-react";
import {
  createShareLinkAction,
  revokeShareLinkAction,
} from "@/app/cases/[id]/share-actions";
import type { AuditEvent } from "@/lib/api-client";

type ShareManagementPanelProps = {
  caseId: string;
  shareToken?: string;
  shareAudience?: string;
  shareRevoked: boolean;
  auditEvents: AuditEvent[];
};

export function ShareManagementPanel({
  caseId,
  shareToken,
  shareAudience,
  shareRevoked,
  auditEvents,
}: ShareManagementPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [auditEventType, setAuditEventType] = useState("all");
  const shareUrl = shareToken ? `/share/${shareToken}` : "";
  const filteredAuditEvents =
    auditEventType === "all"
      ? auditEvents
      : auditEvents.filter((event) => event.eventType === auditEventType);
  const visibleAuditEvents = filteredAuditEvents.slice(-8).reverse();

  return (
    <section className="bg-white px-4 py-5 shadow-panel sm:px-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-ink">Share management</h2>
          <p className="mt-1 text-sm text-slate-600">
            Create limited links for coach, athlete, or guardian status views.
          </p>
        </div>
        <button
          className="inline-flex min-h-10 items-center gap-2 bg-pine px-3 py-2 text-sm font-semibold text-white"
          onClick={() => setIsOpen(true)}
          type="button"
        >
          <Share2 aria-hidden="true" className="h-4 w-4" />
          Create share link
        </button>
      </div>

      {shareToken ? (
        <div className="mt-5 border border-mist bg-field p-4">
          <p className="text-sm font-semibold text-ink">
            {titleCase(shareAudience ?? "share")} link created
          </p>
          <label className="mt-3 block text-sm font-medium text-slate-700">
            Share URL
            <input
              className="mt-1 w-full border border-mist bg-white px-3 py-2 text-sm text-ink"
              readOnly
              value={shareUrl}
            />
          </label>
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              className="inline-flex min-h-10 items-center gap-2 border border-pine px-3 py-2 text-sm font-semibold text-pine"
              onClick={() => void navigator.clipboard?.writeText(shareUrl)}
              type="button"
            >
              <Copy aria-hidden="true" className="h-4 w-4" />
              Copy link
            </button>
            <form action={revokeShareLinkAction}>
              <input name="case_id" type="hidden" value={caseId} />
              <input name="share_token" type="hidden" value={shareToken} />
              <button className="inline-flex min-h-10 items-center gap-2 bg-rust px-3 py-2 text-sm font-semibold text-white">
                <X aria-hidden="true" className="h-4 w-4" />
                Revoke link
              </button>
            </form>
          </div>
        </div>
      ) : null}

      {shareRevoked ? (
        <p className="mt-4 border border-rust/25 bg-rust/10 px-3 py-2 text-sm font-semibold text-rust">
          Share link revoked.
        </p>
      ) : null}

      <div className="mt-5">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <h3 className="text-sm font-semibold text-ink">Audit log</h3>
          <div>
            <label
              className="text-xs font-semibold text-slate-600"
              htmlFor="audit-event-type-filter"
            >
              Audit event type
            </label>
            <div className="mt-1 flex items-center gap-2 border border-mist bg-white px-2 py-1.5">
              <Filter aria-hidden="true" className="h-3.5 w-3.5 text-pine" />
              <select
                id="audit-event-type-filter"
                className="bg-transparent text-sm font-semibold text-ink outline-none"
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
          </div>
        </div>
        {visibleAuditEvents.length > 0 ? (
          <ul className="mt-3 divide-y divide-mist border-y border-mist">
            {visibleAuditEvents.map((event) => (
              <li key={event.id} className="py-3 text-sm">
                <div className="flex items-start justify-between gap-3">
                  <span className="font-semibold text-ink">{event.eventType}</span>
                  <span className="shrink-0 text-xs font-semibold text-slate-500">
                    {event.occurredAt}
                  </span>
                </div>
                <p className="mt-1 text-xs text-slate-600">Actor: {event.actorId}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-2 text-sm text-slate-600">No matching audit events recorded.</p>
        )}
      </div>

      {isOpen ? (
        <div className="fixed inset-0 z-50 grid place-items-center bg-ink/60 px-4 py-6">
          <div
            aria-modal="true"
            className="max-h-full w-full max-w-lg overflow-y-auto bg-white p-5 shadow-panel"
            role="dialog"
            aria-labelledby="create-share-link-title"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 id="create-share-link-title" className="text-lg font-semibold text-ink">
                  Create limited share link
                </h3>
                <p className="mt-1 text-sm text-slate-600">
                  Shared views exclude clinical evidence and private case detail.
                </p>
              </div>
              <button
                aria-label="Close create share link"
                className="inline-flex h-9 w-9 items-center justify-center border border-mist text-slate-600"
                onClick={() => setIsOpen(false)}
                type="button"
              >
                <X aria-hidden="true" className="h-4 w-4" />
              </button>
            </div>
            <form action={createShareLinkAction} className="mt-5 grid gap-3">
              <input name="case_id" type="hidden" value={caseId} />
              <label className="block text-sm font-medium text-slate-700">
                Audience
                <select className="mt-1 w-full border border-mist px-3 py-2" name="audience">
                  <option value="coach">Coach</option>
                  <option value="athlete">Athlete</option>
                  <option value="guardian">Guardian</option>
                </select>
              </label>
              <label className="block text-sm font-medium text-slate-700">
                Allowed activities
                <textarea className="mt-1 min-h-20 w-full border border-mist px-3 py-2" name="allowed_activities" required />
              </label>
              <label className="block text-sm font-medium text-slate-700">
                Restricted activities
                <textarea className="mt-1 min-h-20 w-full border border-mist px-3 py-2" name="restricted_activities" required />
              </label>
              <div className="grid gap-3 sm:grid-cols-2">
                <label className="block text-sm font-medium text-slate-700">
                  Expires in days
                  <input className="mt-1 w-full border border-mist px-3 py-2" defaultValue="7" max="90" min="1" name="expires_in_days" required type="number" />
                </label>
                <label className="block text-sm font-medium text-slate-700">
                  Next review date
                  <input className="mt-1 w-full border border-mist px-3 py-2" name="next_review_date" type="date" />
                </label>
              </div>
              <label className="block text-sm font-medium text-slate-700">
                Share note
                <textarea className="mt-1 min-h-20 w-full border border-mist px-3 py-2" name="clinician_note" required />
              </label>
              <button className="inline-flex min-h-10 items-center justify-center gap-2 bg-pine px-4 text-sm font-semibold text-white">
                <Link2 aria-hidden="true" className="h-4 w-4" />
                Create limited link
              </button>
            </form>
          </div>
        </div>
      ) : null}
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

function titleCase(value: string): string {
  return value.replace(/\b\w/g, (match) => match.toUpperCase());
}

function formatEventType(value: string): string {
  return value.replaceAll("_", " ").replace(/\b\w/g, (match) => match.toUpperCase());
}
