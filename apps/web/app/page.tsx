import { ClipboardList, ShieldCheck } from "lucide-react";
import { RosterTable } from "@/components/roster-table";

export default function DashboardPage() {
  return (
    <main>
      <section className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid gap-6 lg:grid-cols-[1fr_340px] lg:items-end">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-pine">Clinician workspace</p>
            <h1 className="mt-2 text-3xl font-semibold text-ink sm:text-4xl">Return-to-play tracker</h1>
            <p className="mt-3 max-w-3xl text-base text-slate-600">
              Track staged progress, evidence, symptoms, workload, and human decisions without implying automatic clearance.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-white p-4 shadow-panel">
              <ClipboardList aria-hidden="true" className="h-5 w-5 text-pine" />
              <p className="mt-3 text-2xl font-semibold text-ink">3</p>
              <p className="text-sm text-slate-600">Active cases</p>
            </div>
            <div className="bg-white p-4 shadow-panel">
              <ShieldCheck aria-hidden="true" className="h-5 w-5 text-rust" />
              <p className="mt-3 text-2xl font-semibold text-ink">4</p>
              <p className="text-sm text-slate-600">Missing gates</p>
            </div>
          </div>
        </div>
      </section>
      <RosterTable />
    </main>
  );
}
