import type { Milestone } from "@/lib/demo-data";
import { StatusBadge } from "./status-badge";

export function MilestoneChecklist({ milestones }: { milestones: Milestone[] }) {
  return (
    <section className="rp-detail-card">
      <div className="rp-detail-card-header">
        <div>
          <h2>Milestone checklist</h2>
          <p>{milestones.length} current phase gates</p>
        </div>
      </div>
      <div className="rp-milestone-list">
        {milestones.map((milestone) => (
          <div key={milestone.id} className="rp-milestone-row">
            <div>
              <p>{milestone.title}</p>
              <span>{milestone.kind} - {milestone.required ? "Required" : "Optional"}</span>
            </div>
            <StatusBadge status={milestone.status} />
          </div>
        ))}
      </div>
    </section>
  );
}
