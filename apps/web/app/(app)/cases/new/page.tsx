import Link from "next/link";
import { ArrowLeft, Pencil } from "lucide-react";
import { ErrorState, UnauthorizedState } from "@/components/state-panels";
import { getCaseCreationData, UnauthorizedApiError } from "@/lib/api-client";
import { CaseCreateForm } from "./case-create-form";

export default async function NewCasePage() {
  const data = await loadCaseCreationData();
  if (data.status === "unauthorized") {
    return <UnauthorizedState />;
  }
  if (data.status === "error" || data.source !== "api") {
    return (
      <ErrorState
        title="Case creation unavailable"
        body="The case creation workflow requires an authenticated API data mode."
      />
    );
  }

  return (
    <main className="rp-form-page">
      <header className="rp-form-page-header">
        <Link href="/" className="rp-back-link">
          <ArrowLeft aria-hidden="true" className="h-4 w-4" />
          Roster
        </Link>
        <div className="rp-form-header-split">
          <div>
            <p className="rp-form-kicker">Clinician workflow</p>
            <h1>Create return-to-play case</h1>
            <p className="rp-form-lead">
              Create the athlete profile, open the injury case, and apply the starting plan in one guided submission.
            </p>
          </div>
          <div className="rp-stat-card">
            <p className="rp-stat-card-label">Available templates</p>
            <p className="rp-stat-card-value">{data.templates.length}</p>
            <p className="rp-stat-card-sub">Active staged plans ready to apply.</p>
          </div>
        </div>
      </header>

      <CaseCreateForm templates={data.templates} />

      {data.athletes.length > 0 ? (
        <section className="rp-listing">
          <div className="rp-listing-header">
            <h2>Existing athletes</h2>
          </div>
          <div className="rp-listing-wrap">
            <table className="rp-listing-table">
              <thead>
                <tr>
                  <th>Athlete</th>
                  <th>Sport</th>
                  <th>Guardian</th>
                  <th>Edit</th>
                </tr>
              </thead>
              <tbody>
                {data.athletes.map((athlete) => (
                  <tr key={athlete.id}>
                    <td className="rp-cell-strong">{athlete.name}</td>
                    <td>{athlete.sport}</td>
                    <td>{athlete.guardian_contact ?? "Not recorded"}</td>
                    <td>
                      <Link className="rp-inline-link" href={`/athletes/${athlete.id}/edit`}>
                        <Pencil aria-hidden="true" className="h-4 w-4" />
                        Edit athlete
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}
    </main>
  );
}

async function loadCaseCreationData() {
  try {
    const data = await getCaseCreationData();
    return { status: "ok" as const, ...data };
  } catch (error) {
    if (error instanceof UnauthorizedApiError) {
      return { status: "unauthorized" as const };
    }
    return { status: "error" as const };
  }
}
