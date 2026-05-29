import { Ban, CheckCircle2 } from "lucide-react";
import { recordClearanceDecisionAction } from "@/app/(app)/cases/[id]/clearance-actions";
import { PendingSubmitButton } from "@/components/pending-submit-button";

export function ClearancePanel({
  caseId,
  phaseId,
  restrictions,
  note,
}: {
  caseId: string;
  phaseId: string;
  restrictions: string;
  note: string;
}) {
  return (
    <section className="rp-clearance">
      <h2>Clearance panel</h2>
      <div className="rp-clearance-cards">
        <div className="rp-clearance-card">
          <Ban aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0 text-[var(--rp-warn-dot)]" />
          <div>
            <p>Current restrictions</p>
            <p>{restrictions}</p>
          </div>
        </div>
        <div className="rp-clearance-card">
          <CheckCircle2 aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0 text-[var(--rp-side-text)]" />
          <div>
            <p>Clinician note</p>
            <p>{note}</p>
          </div>
        </div>
      </div>
      <form action={recordClearanceDecisionAction} className="rp-clearance-form">
        <input name="case_id" type="hidden" value={caseId} />
        <input name="phase_id" type="hidden" value={phaseId} />
        <label>
          Decision
          <select name="decision">
            <option value="hold">Hold</option>
            <option value="advance">Advance phase</option>
            <option value="clear_full">Full clearance</option>
            <option value="close_case">Close case</option>
          </select>
        </label>
        <label>
          Rationale
          <textarea name="rationale" required />
        </label>
        <label>
          Restrictions
          <textarea name="restrictions" />
        </label>
        <PendingSubmitButton
          icon={<Ban aria-hidden="true" className="h-4 w-4" />}
          label="Record clearance decision"
          pendingLabel="Recording clearance decision..."
          tone="gold"
        />
      </form>
    </section>
  );
}
