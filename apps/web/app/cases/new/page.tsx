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
    <main>
      <section className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <Link href="/" className="inline-flex min-h-10 items-center gap-2 text-sm font-semibold text-pine">
          <ArrowLeft aria-hidden="true" className="h-4 w-4" />
          Roster
        </Link>
        <div className="mt-5 grid gap-6 lg:grid-cols-[1fr_360px] lg:items-end">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-pine">Clinician workflow</p>
            <h1 className="mt-2 text-3xl font-semibold text-ink sm:text-4xl">Create return-to-play case</h1>
            <p className="mt-3 max-w-3xl text-base text-slate-600">
              Create the athlete profile, open the injury case, and apply the starting plan in one guided submission.
            </p>
          </div>
          <div className="bg-white p-4 shadow-panel">
            <p className="text-sm font-semibold text-ink">Available templates</p>
            <p className="mt-2 text-3xl font-semibold text-pine">{data.templates.length}</p>
            <p className="mt-1 text-sm text-slate-600">Active staged plans ready to apply.</p>
          </div>
        </div>
      </section>

      <CaseCreateForm templates={data.templates} />

      {data.athletes.length > 0 ? (
        <section className="border-t border-mist bg-white">
          <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
            <h2 className="text-lg font-semibold text-ink">Existing athletes</h2>
            <div className="mt-4 overflow-x-auto">
              <table className="w-full min-w-[680px] border-collapse text-left text-sm">
                <thead>
                  <tr className="border-b border-mist text-xs uppercase tracking-wide text-slate-500">
                    <th className="py-3 pr-4 font-semibold">Athlete</th>
                    <th className="px-4 py-3 font-semibold">Sport</th>
                    <th className="px-4 py-3 font-semibold">Guardian</th>
                    <th className="py-3 pl-4 font-semibold">Edit</th>
                  </tr>
                </thead>
                <tbody>
                  {data.athletes.map((athlete) => (
                    <tr key={athlete.id} className="border-b border-mist/70 last:border-0">
                      <td className="py-4 pr-4 font-semibold text-ink">{athlete.name}</td>
                      <td className="px-4 py-4 text-slate-700">{athlete.sport}</td>
                      <td className="px-4 py-4 text-slate-700">{athlete.guardian_contact ?? "Not recorded"}</td>
                      <td className="py-4 pl-4">
                        <Link
                          className="inline-flex min-h-10 items-center gap-2 font-semibold text-pine"
                          href={`/athletes/${athlete.id}/edit`}
                        >
                          <Pencil aria-hidden="true" className="h-4 w-4" />
                          Edit athlete
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
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
