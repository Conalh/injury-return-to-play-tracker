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
    <main>
      <section className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <Link href="/templates" className="inline-flex min-h-10 items-center gap-2 text-sm font-semibold text-pine">
          <ArrowLeft aria-hidden="true" className="h-4 w-4" />
          Templates
        </Link>
        <div className="mt-5">
          <p className="text-sm font-semibold uppercase tracking-wide text-pine">Template builder</p>
          <h1 className="mt-2 text-3xl font-semibold text-ink sm:text-4xl">Edit template</h1>
          <p className="mt-3 text-base text-slate-600">
            Saving edits creates a new active version and archives the previous version.
          </p>
        </div>
      </section>
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
