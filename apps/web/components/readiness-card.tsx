import { AlertTriangle, FileCheck2 } from "lucide-react";
import type { ReadinessSignal } from "@/lib/demo-data";

export function ReadinessCard({ signals }: { signals: ReadinessSignal[] }) {
  return (
    <section className="rp-detail-card">
      <div className="rp-detail-card-header">
        <div>
          <h2>Readiness signals</h2>
          <p>Evidence state only. Human clearance is required.</p>
        </div>
        <FileCheck2 aria-hidden="true" className="h-5 w-5 text-[var(--rp-accent)]" />
      </div>
      <div className="rp-readiness-list">
        {signals.map((signal) => (
          <div key={`${signal.type}-${signal.source}`} className="rp-readiness-item">
            <div className="flex min-w-0 gap-3">
              <AlertTriangle aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0 text-[var(--rp-bad-fg)]" />
              <div>
                <p>{signal.message}</p>
                <span>{signal.type} - {signal.source}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      <p className="rp-auto-clear-note">Stagewise does not auto-clear athletes.</p>
    </section>
  );
}
