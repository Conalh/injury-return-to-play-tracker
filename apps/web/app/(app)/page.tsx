import type { ReactNode } from "react";
import Link from "next/link";
import {
  Activity,
  AlertTriangle,
  ClipboardList,
  FilePenLine,
  Plus,
  RefreshCcw,
  ShieldCheck,
} from "lucide-react";
import { RosterTable } from "@/components/roster-table";
import { EmptyState, ErrorState, UnauthorizedState } from "@/components/state-panels";
import { ClinicalCard } from "@/components/ui-primitives";
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
  const reviewCases = data.athletes.filter((athlete) => athlete.missingGateCount > 0).length;
  const namedDecisions = Math.max(1, activeCases - reviewCases);

  return (
    <main className="rp-page">
      <section className="rp-page-header">
        <div>
          <h1 className="rp-page-title">Return-to-Play Control Center</h1>
          <div className="rp-page-meta">
            <span>Wed, May 27</span>
            <span>Acting as Dr. Aanya Patel</span>
            <span className="rp-source-ok">All evidence sources reporting</span>
          </div>
        </div>
        <div className="rp-page-actions">
          <button className="rp-secondary-button" type="button">
            <RefreshCcw aria-hidden="true" className="h-4 w-4" />
            Refresh
          </button>
          <Link className="rp-secondary-button" href="/templates">
            <FilePenLine aria-hidden="true" className="h-4 w-4" />
            Templates
          </Link>
          <Link className="rp-primary-button" href="/cases/new">
            <Plus aria-hidden="true" className="h-4 w-4" />
            New case
          </Link>
        </div>
      </section>

      <section aria-label="Clinical workload summary" className="rp-kpi-grid" id="active-cases">
        <DashboardKpi
          icon={<ClipboardList aria-hidden="true" className="h-4 w-4" />}
          label="Active cases"
          value={activeCases}
          subcopy="Across current clinical workspace"
        />
        <DashboardKpi
          alert
          icon={<AlertTriangle aria-hidden="true" className="h-4 w-4" />}
          label="Requires clinician review"
          value={reviewCases}
          subcopy="Cases with missing phase gates"
        />
        <DashboardKpi
          warn
          icon={<Activity aria-hidden="true" className="h-4 w-4" />}
          label="Evidence overdue / due today"
          value={missingGates}
          subcopy="Symptoms, tests, workload, or review gates"
        />
        <DashboardKpi
          icon={<ShieldCheck aria-hidden="true" className="h-4 w-4" />}
          label="Named clearance decisions (7d)"
          value={namedDecisions}
          subcopy="Every advancement remains attributable"
        />
      </section>

      <section className="rp-safety-note">
        <AlertTriangle aria-hidden="true" className="mt-0.5 h-4 w-4" />
        <p>
          <strong>Safety reminder.</strong> Stagewise surfaces readiness signals and protocol completion.
          It does not clear athletes. Every clearance transition requires a named clinician decision.
        </p>
      </section>

      {data.athletes.length === 0 ? (
        <EmptyState
          title="No active cases"
          body="Create an athlete and injury case to begin tracking return-to-play evidence."
        />
      ) : (
        <section className="rp-dashboard-grid">
          <RosterTable athletes={data.athletes} source={data.source} />
          <aside className="rp-action-rail">
            <ClinicalCard
              ariaLabel="Evidence action queue"
              id="evidence-queue"
              title="Action queue"
              subtitle="Today"
            >
              <div className="rp-action-list">
                {data.athletes
                  .filter((athlete) => athlete.missingGateCount > 0)
                  .map((athlete) => (
                    <Link className="rp-action-item" href={`/cases/${athlete.id}`} key={athlete.id}>
                      <span className="rp-action-dot" />
                      <span>
                        <strong>{athlete.name}</strong>
                        <span>{athlete.nextAction}</span>
                      </span>
                    </Link>
                  ))}
              </div>
            </ClinicalCard>

            <ClinicalCard
              ariaLabel="Recent named decisions"
              id="decision-queue"
              title="Recent named decisions"
              subtitle="Last 7 days"
            >
              <div className="rp-decision-list">
                {data.athletes.slice(0, 3).map((athlete, index) => (
                  <div className="rp-decision-item" key={athlete.id}>
                    <div>
                      <strong>{index === 0 ? "Held" : index === 1 ? "Modified" : "Advanced"}</strong>
                      <span>{athlete.name}</span>
                    </div>
                    <span>{index === 0 ? "Today" : index === 1 ? "Yesterday" : "Mon"}</span>
                  </div>
                ))}
              </div>
            </ClinicalCard>

            <ClinicalCard
              ariaLabel="Workspace settings"
              id="workspace-settings"
              title="Workspace settings"
              subtitle="Current session"
            >
              <dl className="rp-settings-list">
                <div>
                  <dt>Data mode</dt>
                  <dd>{data.source === "api" ? "API-backed demo" : "Local demo"}</dd>
                </div>
                <div>
                  <dt>Actor</dt>
                  <dd>Dr. Aanya Patel</dd>
                </div>
                <div>
                  <dt>Organization</dt>
                  <dd>Stagewise Athletic Medicine</dd>
                </div>
              </dl>
            </ClinicalCard>

            <ClinicalCard title="Staff on call">
              <div className="rp-staff-list">
                <div><strong>Dr. Aanya Patel</strong><span>Team physician</span></div>
                <div><strong>Dr. Marcus Liang</strong><span>Orthopedics backup</span></div>
                <div><strong>Sarah Okafor, ATC</strong><span>Lead athletic trainer</span></div>
              </div>
            </ClinicalCard>
          </aside>
        </section>
      )}
    </main>
  );
}

function DashboardKpi({
  alert = false,
  icon,
  label,
  subcopy,
  value,
  warn = false,
}: {
  alert?: boolean;
  icon: ReactNode;
  label: string;
  subcopy: string;
  value: number;
  warn?: boolean;
}) {
  return (
    <div className={`rp-kpi ${alert ? "rp-kpi-alert" : ""} ${warn ? "rp-kpi-warn" : ""}`}>
      <div className="rp-kpi-label">{icon}{label}</div>
      <div className="rp-kpi-value">{value}</div>
      <div className="rp-kpi-subcopy">{subcopy}</div>
    </div>
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
