import { Ban, CheckCircle2 } from "lucide-react";
import { recordClearanceDecisionAction } from "@/app/cases/[id]/clearance-actions";

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
    <section className="bg-ink px-4 py-5 text-white shadow-panel sm:px-5">
      <h2 className="text-base font-semibold">Clearance panel</h2>
      <div className="mt-4 grid gap-4">
        <div className="border border-white/15 bg-white/5 p-4">
          <div className="flex gap-3">
            <Ban aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0 text-gold" />
            <div>
              <p className="text-sm font-semibold">Current restrictions</p>
              <p className="mt-1 text-sm text-white/75">{restrictions}</p>
            </div>
          </div>
        </div>
        <div className="border border-white/15 bg-white/5 p-4">
          <div className="flex gap-3">
            <CheckCircle2 aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0 text-mist" />
            <div>
              <p className="text-sm font-semibold">Clinician note</p>
              <p className="mt-1 text-sm text-white/75">{note}</p>
            </div>
          </div>
        </div>
      </div>
      <form action={recordClearanceDecisionAction} className="mt-5 grid gap-3">
        <input name="case_id" type="hidden" value={caseId} />
        <input name="phase_id" type="hidden" value={phaseId} />
        <label className="block text-sm font-medium">
          Decision
          <select
            className="mt-1 w-full border border-white/20 bg-white px-3 py-2 text-sm text-ink outline-none focus:border-gold focus:ring-2 focus:ring-gold/30"
            name="decision"
          >
            <option value="hold">Hold</option>
            <option value="advance">Advance phase</option>
            <option value="clear_full">Full clearance</option>
            <option value="close_case">Close case</option>
          </select>
        </label>
        <label className="block text-sm font-medium">
          Rationale
          <textarea
            className="mt-1 min-h-20 w-full resize-y border border-white/20 bg-white px-3 py-2 text-sm text-ink outline-none focus:border-gold focus:ring-2 focus:ring-gold/30"
            name="rationale"
            required
          />
        </label>
        <label className="block text-sm font-medium">
          Restrictions
          <textarea
            className="mt-1 min-h-20 w-full resize-y border border-white/20 bg-white px-3 py-2 text-sm text-ink outline-none focus:border-gold focus:ring-2 focus:ring-gold/30"
            name="restrictions"
          />
        </label>
        <button className="inline-flex min-h-10 items-center justify-center gap-2 bg-gold px-4 text-sm font-semibold text-ink">
          <Ban aria-hidden="true" className="h-4 w-4" />
          Record clearance decision
        </button>
      </form>
    </section>
  );
}
