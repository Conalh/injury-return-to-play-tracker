import Link from "next/link";
import { ArrowRight, AlertTriangle } from "lucide-react";
import { AthleteAvatar, ClinicalBadge } from "@/components/ui-primitives";
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
      className="rp-roster-card"
      data-source={source}
      data-testid="roster-table"
    >
      <div className="rp-roster-inner">
        <div className="rp-roster-header">
          <div>
            <h2>Active roster</h2>
            <p>Cases needing phase, evidence, or clearance review.</p>
          </div>
          <div className="rp-roster-attention">
            <AlertTriangle aria-hidden="true" className="h-4 w-4" />
            {attentionItems} attention items
          </div>
        </div>

        <div className="rp-table-wrap">
          <table className="rp-table">
            <thead>
              <tr>
                <th>Athlete</th>
                <th>Active injury</th>
                <th>Current phase</th>
                <th>Symptoms</th>
                <th>Missing gates</th>
                <th>Participation</th>
                <th>Next action</th>
              </tr>
            </thead>
            <tbody>
              {athletes.map((athlete) => (
                <tr key={athlete.id}>
                  <td>
                    <Link
                      href={`/cases/${athlete.id}`}
                      className="rp-athlete-link"
                    >
                      <AthleteAvatar id={athlete.id} name={athlete.name} size="md" />
                      <span>
                        <strong>{athlete.name}</strong>
                        <span>{athlete.sport} - {athlete.position}</span>
                      </span>
                      <ArrowRight
                        aria-hidden="true"
                        className="h-4 w-4"
                      />
                    </Link>
                  </td>
                  <td>{athlete.activeInjury}</td>
                  <td>
                    <div className="rp-phase-cell">{athlete.currentPhase}</div>
                    <div className="rp-muted">{athlete.daysInPhase} days in phase</div>
                  </td>
                  <td>{athlete.latestSymptomStatus}</td>
                  <td>
                    <ClinicalBadge tone={athlete.missingGateCount > 0 ? "warn" : "ok"}>
                      {athlete.missingGateCount}
                    </ClinicalBadge>
                  </td>
                  <td><ClinicalBadge tone="info">{athlete.participationStatus}</ClinicalBadge></td>
                  <td>{athlete.nextAction}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
