"use client";

import { useState } from "react";
import { Copy, Link2, Share2, X } from "lucide-react";
import {
  createShareLinkAction,
  revokeShareLinkAction,
} from "@/app/(app)/cases/[id]/share-actions";
import { PendingSubmitButton } from "@/components/pending-submit-button";
import { Tooltip } from "@/components/ui-primitives";

type ShareManagementPanelProps = {
  caseId: string;
  shareToken?: string;
  shareAudience?: string;
  shareRevoked: boolean;
};

export function ShareManagementPanel({
  caseId,
  shareToken,
  shareAudience,
  shareRevoked,
}: ShareManagementPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const shareUrl = shareToken ? `/share/${shareToken}` : "";

  return (
    <section className="rp-detail-card">
      <div className="rp-detail-card-header">
        <div>
          <h2>Share management</h2>
          <p>Create limited links for coach, athlete, or guardian status views.</p>
        </div>
        <Tooltip label="Create a limited status view for a coach, athlete, or guardian">
          <button className="rp-primary-button" onClick={() => setIsOpen(true)} type="button">
            <Share2 aria-hidden="true" className="h-4 w-4" />
            Create share link
          </button>
        </Tooltip>
      </div>

      {shareToken || shareRevoked ? (
        <div className="rp-entry-body">
          {shareToken ? (
            <div className="rp-subform">
              <p className="rp-share-result-title">
                {titleCase(shareAudience ?? "share")} link created
              </p>
              <label className="rp-field">
                Share URL
                <input readOnly value={shareUrl} />
              </label>
              <div className="rp-share-actions">
                <Tooltip label="Copy the limited share URL">
                  <button
                    className="rp-secondary-button"
                    onClick={() => void navigator.clipboard?.writeText(shareUrl)}
                    type="button"
                  >
                    <Copy aria-hidden="true" className="h-4 w-4" />
                    Copy link
                  </button>
                </Tooltip>
                <form action={revokeShareLinkAction}>
                  <input name="case_id" type="hidden" value={caseId} />
                  <input name="share_token" type="hidden" value={shareToken} />
                  <Tooltip label="Immediately disable this external access link">
                    <PendingSubmitButton
                      icon={<X aria-hidden="true" className="h-4 w-4" />}
                      label="Revoke link"
                      pendingLabel="Revoking link..."
                      tone="rust"
                    />
                  </Tooltip>
                </form>
              </div>
            </div>
          ) : null}

          {shareRevoked ? (
            <p className="rp-form-banner rp-form-banner-bad">Share link revoked.</p>
          ) : null}
        </div>
      ) : null}

      {isOpen ? (
        <div className="rp-modal-overlay">
          <div
            aria-modal="true"
            className="rp-modal"
            role="dialog"
            aria-labelledby="create-share-link-title"
          >
            <div className="rp-modal-header">
              <div>
                <h3 id="create-share-link-title">Create limited share link</h3>
                <p>Shared views exclude clinical evidence and private case detail.</p>
              </div>
              <Tooltip label="Close share link dialog">
                <button
                  aria-label="Close create share link"
                  className="rp-icon-button"
                  onClick={() => setIsOpen(false)}
                  type="button"
                >
                  <X aria-hidden="true" className="h-4 w-4" />
                </button>
              </Tooltip>
            </div>
            <form action={createShareLinkAction} className="rp-modal-form">
              <input name="case_id" type="hidden" value={caseId} />
              <label className="rp-field">
                Audience
                <select name="audience">
                  <option value="coach">Coach</option>
                  <option value="athlete">Athlete</option>
                  <option value="guardian">Guardian</option>
                </select>
              </label>
              <label className="rp-field">
                Allowed activities
                <textarea name="allowed_activities" required />
              </label>
              <label className="rp-field">
                Restricted activities
                <textarea name="restricted_activities" required />
              </label>
              <div className="rp-form-grid rp-form-grid-2">
                <label className="rp-field">
                  Expires in days
                  <input defaultValue="7" max="90" min="1" name="expires_in_days" required type="number" />
                </label>
                <label className="rp-field">
                  Next review date
                  <input name="next_review_date" type="date" />
                </label>
              </div>
              <label className="rp-field">
                Share note
                <textarea name="clinician_note" required />
              </label>
              <PendingSubmitButton
                icon={<Link2 aria-hidden="true" className="h-4 w-4" />}
                label="Create limited link"
                pendingLabel="Creating limited link..."
              />
            </form>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function titleCase(value: string): string {
  return value.replace(/\b\w/g, (match) => match.toUpperCase());
}
