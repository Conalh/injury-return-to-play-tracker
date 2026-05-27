import type { Phase } from "@/lib/demo-data";
import { StatusBadge } from "./status-badge";

export function PhaseTimeline({ phases }: { phases: Phase[] }) {
  return (
    <section className="bg-white px-4 py-5 shadow-panel sm:px-5">
      <h2 className="text-base font-semibold text-ink">Phase timeline</h2>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {phases.map((phase) => (
          <div key={phase.id} className="min-w-0 border-l-4 border-pine bg-field p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  {phase.status === "current" ? "Current phase" : "Next phase"}
                </p>
                <h3 className="mt-1 text-lg font-semibold text-ink">{phase.name}</h3>
              </div>
              <StatusBadge status={phase.status} />
            </div>
            <p className="mt-3 break-words text-sm text-slate-600">{phase.objective}</p>
            <p className="mt-3 text-xs font-semibold text-slate-500">{phase.days} days tracked</p>
          </div>
        ))}
      </div>
    </section>
  );
}
