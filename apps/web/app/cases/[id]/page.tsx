import Link from "next/link";
import { ArrowLeft, CalendarDays, ShieldAlert } from "lucide-react";
import { ClearancePanel } from "@/components/clearance-panel";
import { FunctionalTestTable, SymptomTrend, WorkloadProgression } from "@/components/evidence-panels";
import { MilestoneChecklist } from "@/components/milestone-checklist";
import { PhaseTimeline } from "@/components/phase-timeline";
import { ReadinessCard } from "@/components/readiness-card";
import { getCaseDetail } from "@/lib/demo-data";

export default async function CaseDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const detail = getCaseDetail(id);
  const currentPhase = detail.phases.find((phase) => phase.status === "current") ?? detail.phases[0];

  return (
    <main>
      <section className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <Link href="/" className="inline-flex min-h-10 items-center gap-2 text-sm font-semibold text-pine">
          <ArrowLeft aria-hidden="true" className="h-4 w-4" />
          Roster
        </Link>
        <div className="mt-5 grid gap-6 lg:grid-cols-[1fr_360px] lg:items-start">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-pine">{detail.athlete.sport} · {detail.athlete.position}</p>
            <h1 className="mt-2 text-3xl font-semibold text-ink sm:text-4xl">{detail.athlete.name}</h1>
            <p className="mt-3 max-w-3xl text-base text-slate-600">{detail.summary}</p>
          </div>
          <div className="bg-white p-4 shadow-panel">
            <div className="flex items-start gap-3">
              <ShieldAlert aria-hidden="true" className="mt-0.5 h-5 w-5 text-rust" />
              <div>
                <p className="font-semibold text-ink">{detail.injuryTitle}</p>
                <p className="mt-1 text-sm text-slate-600">{detail.athlete.participationStatus}</p>
              </div>
            </div>
            <div className="mt-4 flex items-center gap-2 text-sm text-slate-600">
              <CalendarDays aria-hidden="true" className="h-4 w-4 text-pine" />
              {detail.athlete.daysInPhase} days in current phase
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-5 px-4 pb-8 sm:px-6 lg:grid-cols-[minmax(0,1fr)_360px] lg:px-8">
        <div className="grid min-w-0 gap-5">
          <PhaseTimeline phases={detail.phases} />
          <MilestoneChecklist milestones={currentPhase.milestones} />
          <div className="grid min-w-0 gap-5 xl:grid-cols-2">
            <SymptomTrend symptomLogs={detail.symptomLogs} />
            <FunctionalTestTable functionalTests={detail.functionalTests} />
          </div>
          <WorkloadProgression workloadSessions={detail.workloadSessions} />
        </div>
        <div className="grid min-w-0 content-start gap-5">
          <ReadinessCard signals={detail.readinessSignals} />
          <ClearancePanel restrictions={detail.restrictions} note={detail.clinicianNote} />
        </div>
      </section>
    </main>
  );
}
