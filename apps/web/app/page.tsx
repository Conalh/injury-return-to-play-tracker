import Link from "next/link";
import { ClipboardList, FilePenLine, Plus, ShieldCheck } from "lucide-react";
import { RosterTable } from "@/components/roster-table";
import { EmptyState, ErrorState, UnauthorizedState } from "@/components/state-panels";
import { getDashboardData, UnauthorizedApiError } from "@/lib/api-client";

export default async function DashboardPage() {
  const data = await loadDashboardData();
  if (data.status === "unauthorized") {
    return <UnauthorizedState />;
  }
  if (data.status === "error") {
    return (
      <ErrorState
        title="Workspace unavailable"
        body="The return-to-play API could not be reached for this dashboard."
      />
    );
  }

  const activeCases = data.athletes.length;
  const missingGates = data.athletes.reduce(
    (total, athlete) => total + athlete.missingGateCount,
    0,
  );

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
            <div className="mt-5 flex flex-wrap gap-3">
              <Link
                className="inline-flex min-h-11 items-center gap-2 bg-pine px-5 text-sm font-semibold text-white shadow-panel"
                href="/cases/new"
              >
                <Plus aria-hidden="true" className="h-4 w-4" />
                New case
              </Link>
              <Link
                className="inline-flex min-h-11 items-center gap-2 border border-pine bg-white px-5 text-sm font-semibold text-pine shadow-panel"
                href="/templates"
              >
                <FilePenLine aria-hidden="true" className="h-4 w-4" />
                Templates
              </Link>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-white p-4 shadow-panel">
              <ClipboardList aria-hidden="true" className="h-5 w-5 text-pine" />
              <p className="mt-3 text-2xl font-semibold text-ink">{activeCases}</p>
              <p className="text-sm text-slate-600">Active cases</p>
            </div>
            <div className="bg-white p-4 shadow-panel">
              <ShieldCheck aria-hidden="true" className="h-5 w-5 text-rust" />
              <p className="mt-3 text-2xl font-semibold text-ink">{missingGates}</p>
              <p className="text-sm text-slate-600">Missing gates</p>
            </div>
          </div>
        </div>
      </section>
      {data.athletes.length === 0 ? (
        <EmptyState
          title="No active cases"
          body="Create an athlete and injury case to begin tracking return-to-play evidence."
        />
      ) : (
        <RosterTable athletes={data.athletes} source={data.source} />
      )}
    </main>
  );
}

async function loadDashboardData() {
  try {
    const data = await getDashboardData();
    return { status: "ok" as const, ...data };
  } catch (error) {
    if (error instanceof UnauthorizedApiError) {
      return { status: "unauthorized" as const };
    }
    return { status: "error" as const };
  }
}
