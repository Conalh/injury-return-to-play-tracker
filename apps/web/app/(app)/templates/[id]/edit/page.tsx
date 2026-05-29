import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { ErrorState, UnauthorizedState } from "@/components/state-panels";
import { getTemplatePageData, UnauthorizedApiError } from "@/lib/api-client";
import { TemplateForm } from "../../template-form";

export default async function EditTemplatePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const data = await loadTemplatePageData(id);
  if (data.status === "unauthorized") {
    return <UnauthorizedState />;
  }
  if (data.status === "error") {
    return (
      <ErrorState
        title="Template unavailable"
        body="The template could not be loaded from the return-to-play API."
      />
    );
  }

  return (
    <main className="rp-form-page">
      <header className="rp-form-page-header">
        <Link href="/templates" className="rp-back-link">
          <ArrowLeft aria-hidden="true" className="h-4 w-4" />
          Templates
        </Link>
        <p className="rp-form-kicker">Template builder</p>
        <h1>Edit template</h1>
        <p className="rp-form-lead">
          Saving edits creates a new active version and archives the previous version.
        </p>
      </header>
      <TemplateForm template={data.template} />
    </main>
  );
}

async function loadTemplatePageData(templateId: string) {
  try {
    const data = await getTemplatePageData(templateId);
    return { status: "ok" as const, ...data };
  } catch (error) {
    if (error instanceof UnauthorizedApiError) {
      return { status: "unauthorized" as const };
    }
    return { status: "error" as const };
  }
}
