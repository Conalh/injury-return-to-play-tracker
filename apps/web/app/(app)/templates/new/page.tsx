import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { TemplateForm } from "../template-form";

export default function NewTemplatePage() {
  return (
    <main className="rp-form-page">
      <header className="rp-form-page-header">
        <Link href="/templates" className="rp-back-link">
          <ArrowLeft aria-hidden="true" className="h-4 w-4" />
          Templates
        </Link>
        <p className="rp-form-kicker">Template builder</p>
        <h1>New return-plan template</h1>
      </header>
      <TemplateForm />
    </main>
  );
}
