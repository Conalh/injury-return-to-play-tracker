import Link from "next/link";
import { ArrowRight, AlertTriangle } from "lucide-react";
import type { AthleteSummary } from "@/lib/demo-data";
import type { DataSource } from "@/lib/api-client";

export function RosterTable({
  athletes,
  source,
}: {
  athletes: AthleteSummary[];
  source: DataSource;
}) {
  const attentionItems = athletes.reduce(
    (total, athlete) => total + athlete.missingGateCount,
    0,
  );

  return (
    <section
      className="overflow-hidden border-y border-mist bg-white"
      data-source={source}
      data-testid="roster-table"
    >
      <div className="mx-auto max-w-7xl px-4 py-5 sm:px-6 lg:px-8">
        <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-ink">Active roster</h2>
            <p className="text-sm text-slate-600">Cases needing phase, evidence, or clearance review.</p>
          </div>
          <div className="flex items-center gap-2 text-sm font-medium text-rust">
            <AlertTriangle aria-hidden="true" className="h-4 w-4" />
            {attentionItems} attention items
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] border-collapse text-left text-sm">
            <thead>
              <tr className="border-b border-mist text-xs uppercase tracking-wide text-slate-500">
                <th className="py-3 pr-4 font-semibold">Athlete</th>
                <th className="px-4 py-3 font-semibold">Active injury</th>
                <th className="px-4 py-3 font-semibold">Current phase</th>
                <th className="px-4 py-3 font-semibold">Symptoms</th>
                <th className="px-4 py-3 font-semibold">Missing gates</th>
                <th className="py-3 pl-4 font-semibold">Next action</th>
              </tr>
            </thead>
            <tbody>
              {athletes.map((athlete) => (
                <tr key={athlete.id} className="border-b border-mist/70 last:border-0">
                  <td className="py-4 pr-4">
                    <Link
                      href={`/cases/${athlete.id}`}
                      className="group inline-flex min-h-10 items-center gap-2 font-semibold text-ink"
                    >
                      {athlete.name}
                      <ArrowRight
                        aria-hidden="true"
                        className="h-4 w-4 text-pine transition-transform group-hover:translate-x-0.5"
                      />
                    </Link>
                    <div className="text-xs text-slate-500">{athlete.sport} · {athlete.position}</div>
                  </td>
                  <td className="px-4 py-4 text-slate-700">{athlete.activeInjury}</td>
                  <td className="px-4 py-4">
                    <div className="font-medium text-ink">{athlete.currentPhase}</div>
                    <div className="text-xs text-slate-500">{athlete.daysInPhase} days in phase</div>
                  </td>
                  <td className="px-4 py-4 text-slate-700">{athlete.latestSymptomStatus}</td>
                  <td className="px-4 py-4">
                    <span className="inline-flex min-w-10 justify-center rounded-md bg-rust/10 px-2 py-1 font-semibold text-rust">
                      {athlete.missingGateCount}
                    </span>
                  </td>
                  <td className="py-4 pl-4 text-slate-700">{athlete.nextAction}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
