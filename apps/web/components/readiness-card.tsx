import { AlertTriangle, FileCheck2 } from "lucide-react";
import type { ReadinessSignal } from "@/lib/demo-data";

export function ReadinessCard({ signals }: { signals: ReadinessSignal[] }) {
  return (
    <section className="bg-white px-4 py-5 shadow-panel sm:px-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-ink">Readiness review</h2>
          <p className="mt-1 text-sm text-slate-600">Evidence state only. Human clearance is required.</p>
        </div>
        <FileCheck2 aria-hidden="true" className="h-5 w-5 text-pine" />
      </div>
      <div className="mt-4 grid gap-3">
        {signals.map((signal) => (
          <div key={`${signal.type}-${signal.source}`} className="border border-mist bg-field p-4">
            <div className="flex gap-3">
              <AlertTriangle aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0 text-rust" />
              <div>
                <p className="font-semibold text-ink">{signal.message}</p>
                <p className="mt-1 text-sm text-slate-600">{signal.type} · {signal.source}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
