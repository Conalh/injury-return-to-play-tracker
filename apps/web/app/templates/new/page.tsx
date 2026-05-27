import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { TemplateForm } from "../template-form";

export default function NewTemplatePage() {
  return (
    <main>
      <section className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <Link href="/templates" className="inline-flex min-h-10 items-center gap-2 text-sm font-semibold text-pine">
          <ArrowLeft aria-hidden="true" className="h-4 w-4" />
          Templates
        </Link>
        <div className="mt-5">
          <p className="text-sm font-semibold uppercase tracking-wide text-pine">Template builder</p>
          <h1 className="mt-2 text-3xl font-semibold text-ink sm:text-4xl">New return-plan template</h1>
        </div>
      </section>
      <TemplateForm />
    </main>
  );
}
