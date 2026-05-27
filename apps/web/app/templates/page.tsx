import Link from "next/link";
import { Archive, FilePenLine, Plus } from "lucide-react";
import { ErrorState, UnauthorizedState } from "@/components/state-panels";
import { getTemplateListData, UnauthorizedApiError } from "@/lib/api-client";
import { archiveTemplateAction } from "./actions";

export default async function TemplatesPage({
  searchParams,
}: {
  searchParams: Promise<{ archived?: string }>;
}) {
  const params = await searchParams;
  const data = await loadTemplateListData();
  if (data.status === "unauthorized") {
    return <UnauthorizedState />;
  }
  if (data.status === "error" || data.source !== "api") {
    return (
      <ErrorState
        title="Templates unavailable"
        body="Template management requires an authenticated API data mode."
      />
    );
  }

  const activeCount = data.templates.filter((template) => template.active).length;

  return (
    <main>
      <section className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="grid gap-6 lg:grid-cols-[1fr_360px] lg:items-end">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-pine">Clinician templates</p>
            <h1 className="mt-2 text-3xl font-semibold text-ink sm:text-4xl">Template builder</h1>
            <p className="mt-3 max-w-3xl text-base text-slate-600">
              Manage reusable staged return-to-play plans before applying them to clinical cases.
            </p>
            <Link
              className="mt-5 inline-flex min-h-11 items-center gap-2 bg-pine px-5 text-sm font-semibold text-white shadow-panel"
              href="/templates/new"
            >
              <Plus aria-hidden="true" className="h-4 w-4" />
              New template
            </Link>
          </div>
          <div className="bg-white p-4 shadow-panel">
            <p className="text-sm font-semibold text-ink">Active templates</p>
            <p className="mt-2 text-3xl font-semibold text-pine">{activeCount}</p>
            <p className="mt-1 text-sm text-slate-600">Available for case creation.</p>
          </div>
        </div>
      </section>

      {params.archived ? (
        <div className="mx-auto max-w-7xl px-4 pb-4 sm:px-6 lg:px-8">
          <div className="border border-pine/30 bg-pine/10 px-4 py-3 text-sm font-medium text-pine">
            {params.archived} archived.
          </div>
        </div>
      ) : null}

      <section className="border-y border-mist bg-white">
        <div className="mx-auto max-w-7xl px-4 py-5 sm:px-6 lg:px-8">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[860px] border-collapse text-left text-sm">
              <thead>
                <tr className="border-b border-mist text-xs uppercase tracking-wide text-slate-500">
                  <th className="py-3 pr-4 font-semibold">Template</th>
                  <th className="px-4 py-3 font-semibold">Category</th>
                  <th className="px-4 py-3 font-semibold">Version</th>
                  <th className="px-4 py-3 font-semibold">Status</th>
                  <th className="py-3 pl-4 font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.templates.map((template) => (
                  <tr key={template.id} className="border-b border-mist/70 last:border-0">
                    <td className="py-4 pr-4">
                      <Link
                        className="inline-flex min-h-10 items-center gap-2 font-semibold text-ink"
                        href={`/templates/${template.id}/edit`}
                      >
                        <FilePenLine aria-hidden="true" className="h-4 w-4 text-pine" />
                        {template.name}
                      </Link>
                      <div className="text-xs text-slate-500">{template.description ?? "No description"}</div>
                    </td>
                    <td className="px-4 py-4 text-slate-700">{template.injury_category}</td>
                    <td className="px-4 py-4 font-semibold text-ink">v{template.version}</td>
                    <td className="px-4 py-4 text-slate-700">{template.active ? "Active" : "Archived"}</td>
                    <td className="py-4 pl-4">
                      {template.active ? (
                        <form action={archiveTemplateAction}>
                          <input name="template_id" type="hidden" value={template.id} />
                          <input name="template_name" type="hidden" value={template.name} />
                          <button
                            aria-label={`Archive ${template.name}`}
                            className="inline-flex min-h-10 items-center gap-2 text-sm font-semibold text-rust"
                            type="submit"
                          >
                            <Archive aria-hidden="true" className="h-4 w-4" />
                            Archive
                          </button>
                        </form>
                      ) : (
                        <span className="text-sm text-slate-500">No actions</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>
  );
}

async function loadTemplateListData() {
  try {
    const data = await getTemplateListData();
    return { status: "ok" as const, ...data };
  } catch (error) {
    if (error instanceof UnauthorizedApiError) {
      return { status: "unauthorized" as const };
    }
    return { status: "error" as const };
  }
}
