import type { Milestone } from "@/lib/demo-data";
import { StatusBadge } from "./status-badge";

export function MilestoneChecklist({ milestones }: { milestones: Milestone[] }) {
  return (
    <section className="bg-white px-4 py-5 shadow-panel sm:px-5">
      <h2 className="text-base font-semibold text-ink">Current phase gates</h2>
      <div className="mt-4 divide-y divide-mist">
        {milestones.map((milestone) => (
          <div key={milestone.id} className="flex items-center justify-between gap-4 py-3 first:pt-0 last:pb-0">
            <div>
              <p className="font-medium text-ink">{milestone.title}</p>
              <p className="text-xs text-slate-500">{milestone.kind} · {milestone.required ? "Required" : "Optional"}</p>
            </div>
            <StatusBadge status={milestone.status} />
          </div>
        ))}
      </div>
    </section>
  );
}
