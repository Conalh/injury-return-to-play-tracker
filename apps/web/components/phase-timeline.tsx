import type { Phase } from "@/lib/demo-data";
import { StatusBadge } from "./status-badge";

export function PhaseTimeline({ phases }: { phases: Phase[] }) {
  return (
    <section className="rp-detail-card">
      <div className="rp-detail-card-header">
        <div>
          <h2>Return-to-play phase progression</h2>
          <p>Protocol phases remain gated by evidence and clinician review.</p>
        </div>
      </div>
      <div className="rp-phase-grid">
        {phases.map((phase) => (
          <div key={phase.id} className="rp-phase-card">
            <div className="rp-phase-card-top">
              <div>
                <p className="rp-phase-kicker">
                  {phase.status === "current"
                    ? "Current phase"
                    : phase.status === "held"
                      ? "Held phase"
                      : "Next phase"}
                </p>
                <h3>{phase.name}</h3>
              </div>
              <StatusBadge status={phase.status} />
            </div>
            <p className="rp-phase-objective">{phase.objective}</p>
            <p className="rp-muted">{phase.days} days tracked</p>
          </div>
        ))}
      </div>
    </section>
  );
}
