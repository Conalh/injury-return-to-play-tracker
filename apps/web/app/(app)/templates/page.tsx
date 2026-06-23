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
  if (data.status === "error") {
    return (
      <ErrorState
        title="Templates unavailable"
        body="The template list could not be loaded from the return-to-play API."
      />
    );
  }

  const isApiMode = data.source === "api";
  const activeCount = data.templates.filter((template) => template.active).length;

  return (
    <main className="rp-form-page">
      <header className="rp-form-page-header">
        <div className="rp-form-header-split">
          <div>
            <p className="rp-form-kicker">Clinician templates</p>
            <h1>Template builder</h1>
            <p className="rp-form-lead">
              Manage reusable staged return-to-play plans before applying them to clinical cases.
            </p>
            <div className="rp-form-header-cta">
              {isApiMode ? (
                <Link className="rp-primary-button" href="/templates/new">
                  <Plus aria-hidden="true" className="h-4 w-4" />
                  New template
                </Link>
              ) : (
                <p className="rp-cell-sub">Read-only local demo templates. API mode enables versioning.</p>
              )}
            </div>
          </div>
          <div className="rp-stat-card">
            <p className="rp-stat-card-label">Active templates</p>
            <p className="rp-stat-card-value">{activeCount}</p>
            <p className="rp-stat-card-sub">Available for case creation.</p>
          </div>
        </div>
      </header>

      {params.archived ? (
        <p className="rp-form-banner">{params.archived} archived.</p>
      ) : null}

      <section className="rp-listing">
        <div className="rp-listing-header">
          <h2>Return-plan templates</h2>
        </div>
        <div className="rp-listing-wrap">
          <table className="rp-listing-table">
            <thead>
              <tr>
                <th>Template</th>
                <th>Category</th>
                <th>Version</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.templates.map((template) => (
                <tr key={template.id}>
                  <td>
                    {isApiMode ? (
                      <Link className="rp-listing-link" href={`/templates/${template.id}/edit`}>
                        <FilePenLine aria-hidden="true" className="h-4 w-4" />
                        {template.name}
                      </Link>
                    ) : (
                      <span className="rp-listing-link">
                        <FilePenLine aria-hidden="true" className="h-4 w-4" />
                        {template.name}
                      </span>
                    )}
                    <div className="rp-cell-sub">{template.description ?? "No description"}</div>
                  </td>
                  <td>{template.injury_category}</td>
                  <td className="rp-cell-strong">v{template.version}</td>
                  <td>{template.active ? "Active" : "Archived"}</td>
                  <td>
                    {template.active && isApiMode ? (
                      <form action={archiveTemplateAction}>
                        <input name="template_id" type="hidden" value={template.id} />
                        <input name="template_name" type="hidden" value={template.name} />
                        <button
                          aria-label={`Archive ${template.name}`}
                          className="rp-inline-danger"
                          type="submit"
                        >
                          <Archive aria-hidden="true" className="h-4 w-4" />
                          Archive
                        </button>
                      </form>
                    ) : template.active ? (
                      <span className="rp-cell-sub">API mode required</span>
                    ) : (
                      <span className="rp-cell-sub">No actions</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
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
