import { Ban, CheckCircle2 } from "lucide-react";

export function ClearancePanel({ restrictions, note }: { restrictions: string; note: string }) {
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
      <button className="mt-5 inline-flex min-h-10 items-center justify-center gap-2 bg-gold px-4 text-sm font-semibold text-ink">
        <Ban aria-hidden="true" className="h-4 w-4" />
        Record hold decision
      </button>
    </section>
  );
}
