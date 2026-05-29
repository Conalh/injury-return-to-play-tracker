import Link from "next/link";
import { ArrowLeft, FileDown, Plus, Share2, ShieldAlert } from "lucide-react";
import { ClearancePanel } from "@/components/clearance-panel";
import { FunctionalTestTable, SymptomTrend, WorkloadProgression } from "@/components/evidence-panels";
import { EvidenceEntryPanel } from "@/components/evidence-entry-panel";
import { MilestoneChecklist } from "@/components/milestone-checklist";
import { PhaseTimeline } from "@/components/phase-timeline";
import { ReadinessCard } from "@/components/readiness-card";
import { ShareManagementPanel } from "@/components/share-management-panel";
import { ErrorState, UnauthorizedState } from "@/components/state-panels";
import { AthleteAvatar, ClinicalBadge, Tooltip } from "@/components/ui-primitives";
import { getCasePageData, UnauthorizedApiError } from "@/lib/api-client";

export default async function CaseDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const { id } = await params;
  const query = await searchParams;
  const data = await loadCasePageData(id);
  if (data.status === "unauthorized") {
    return <UnauthorizedState />;
  }
  if (data.status === "error") {
    return (
      <ErrorState
        title="Case unavailable"
        body="The case detail could not be loaded from the return-to-play API."
      />
    );
  }

  const { auditEvents, detail, source } = data;
  const currentPhase =
    detail.phases.find((phase) => phase.status === "current" || phase.status === "held") ??
    detail.phases[0];
  const shareToken = singleQueryValue(query.share_token);
  const shareAudience = singleQueryValue(query.share_audience);

  return (
    <main className="rp-case-page" data-source={source} data-testid="case-detail">
      <section className="rp-case-header">
        <div className="rp-case-header-top">
          <Link href="/" className="rp-back-link">
            <ArrowLeft aria-hidden="true" className="h-4 w-4" />
            Roster
          </Link>
          <div className="rp-case-actions">
            <Tooltip label="Create or manage limited external access">
              <Link className="rp-secondary-button" href="#share-access">
                <Share2 aria-hidden="true" className="h-4 w-4" />
                Share access
              </Link>
            </Tooltip>
            <Tooltip label="Download a report with status, evidence, and audit metadata">
              <Link className="rp-secondary-button" href={`/cases/${detail.id}/report`}>
                <FileDown aria-hidden="true" className="h-4 w-4" />
                Download PDF report
              </Link>
            </Tooltip>
            <Tooltip label="Record symptoms, tests, workload, or milestone evidence">
              <a className="rp-primary-button" href="#record-evidence">
                <Plus aria-hidden="true" className="h-4 w-4" />
                Add evidence
              </a>
            </Tooltip>
          </div>
        </div>

        <div className="rp-case-hero">
          <AthleteAvatar id={detail.athleteId} name={detail.athlete.name} size="lg" />
          <div className="min-w-0">
            <div className="rp-case-title-row">
              <h1>{detail.athlete.name}</h1>
              <ClinicalBadge tone={currentPhase.status === "held" ? "bad" : "info"}>
                {currentPhase.status === "held" ? "Held phase" : currentPhase.status}
              </ClinicalBadge>
              <ClinicalBadge tone="hold">{detail.athlete.participationStatus}</ClinicalBadge>
            </div>
            <div className="rp-case-meta">
              <span>{detail.athlete.sport} - {detail.athlete.position}</span>
              <span title={detail.id}>Case {caseReference(detail.id)}</span>
              <span>{detail.injuryTitle}</span>
              <span>{detail.athlete.daysInPhase} days in current phase</span>
            </div>
            <p className="rp-case-summary">{detail.summary}</p>
          </div>
        </div>

        <div className="rp-risk-banner">
          <ShieldAlert aria-hidden="true" className="mt-0.5 h-4 w-4" />
          <div>
            <strong>Clinician review required before advancement.</strong>
            <span> Current restrictions and readiness signals are inputs only; this workflow never substitutes for a named clearance decision.</span>
          </div>
        </div>

        <nav aria-label="Case detail sections" className="rp-case-tabs">
          <a href="#overview">Overview</a>
          <a href="#record-evidence">Evidence</a>
          <a href="#clearance">Decisions</a>
          <a href="#share-access">Share access</a>
          <a href="#share-access">Audit history</a>
        </nav>
      </section>

      <section className="rp-case-grid" id="overview">
        <div className="rp-case-main">
          <PhaseTimeline phases={detail.phases} />
          <MilestoneChecklist milestones={currentPhase.milestones} />
          <div className="rp-evidence-grid">
            <SymptomTrend symptomLogs={detail.symptomLogs} />
            <FunctionalTestTable functionalTests={detail.functionalTests} />
          </div>
          <WorkloadProgression workloadSessions={detail.workloadSessions} />
        </div>
        <div className="rp-case-rail">
          <ReadinessCard signals={detail.readinessSignals} />
          <div id="record-evidence">
            <EvidenceEntryPanel
              athleteId={detail.athleteId}
              caseId={detail.id}
              currentPhase={currentPhase}
            />
          </div>
          <div id="clearance">
            <ClearancePanel
              caseId={detail.id}
              phaseId={currentPhase.id}
              restrictions={detail.restrictions}
              note={detail.clinicianNote}
            />
          </div>
          <div id="share-access">
            <ShareManagementPanel
              auditEvents={auditEvents}
              caseId={detail.id}
              shareAudience={shareAudience}
              shareRevoked={singleQueryValue(query.share_revoked) === "1"}
              shareToken={shareToken}
            />
          </div>
        </div>
      </section>
    </main>
  );
}

async function loadCasePageData(caseId: string) {
  try {
    const data = await getCasePageData(caseId);
    return { status: "ok" as const, ...data };
  } catch (error) {
    if (error instanceof UnauthorizedApiError) {
      return { status: "unauthorized" as const };
    }
    return { status: "error" as const };
  }
}

function singleQueryValue(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

// Hosted case IDs end in a 32-char uuid hex, which reads as noise in the UI.
// Show a short, stable reference code; the full id stays in the title tooltip.
function caseReference(id: string): string {
  const tail = id.includes("_") ? id.slice(id.lastIndexOf("_") + 1) : id;
  const handle = /^[0-9a-f]{12,}$/i.test(tail) ? tail.slice(0, 6) : tail;
  return handle.toUpperCase();
}
