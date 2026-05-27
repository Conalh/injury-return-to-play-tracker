"use client";

import { useActionState } from "react";
import { useFormStatus } from "react-dom";
import { CheckCircle2, UserPlus } from "lucide-react";
import type { ApiTemplate } from "@/lib/api-client";
import { createCaseAction, type CaseCreationActionState } from "./actions";

const initialCaseCreationState: CaseCreationActionState = {
  status: "idle",
  message: "",
  fieldErrors: {},
};

export function CaseCreateForm({ templates }: { templates: ApiTemplate[] }) {
  const [state, formAction] = useActionState<CaseCreationActionState, FormData>(
    createCaseAction,
    initialCaseCreationState,
  );

  return (
    <form action={formAction} className="grid gap-6" noValidate>
      {state.status === "error" ? (
        <div className="border border-rust/30 bg-rust/10 px-4 py-3 text-sm text-rust" role="alert">
          {state.message}
        </div>
      ) : null}

      <section className="border-y border-mist bg-white">
        <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[280px_1fr] lg:px-8">
          <div>
            <UserPlus aria-hidden="true" className="h-5 w-5 text-pine" />
            <h2 className="mt-3 text-lg font-semibold text-ink">Athlete profile</h2>
            <p className="mt-1 text-sm text-slate-600">Create the athlete record used for this return-to-play case.</p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Athlete name" name="athlete_name" required state={state} />
            <Field label="Date of birth" name="date_of_birth" type="date" required state={state} />
            <Field label="Sport" name="sport" required state={state} />
            <Field label="Position" name="position" state={state} />
            <Field label="Guardian email" name="guardian_contact" type="email" state={state} />
          </div>
        </div>
      </section>

      <section className="border-y border-mist bg-white">
        <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[280px_1fr] lg:px-8">
          <div>
            <CheckCircle2 aria-hidden="true" className="h-5 w-5 text-pine" />
            <h2 className="mt-3 text-lg font-semibold text-ink">Case and template</h2>
            <p className="mt-1 text-sm text-slate-600">Open the injury case and apply the initial staged plan.</p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Case title" name="case_title" required state={state} />
            <Field label="Injury category" name="injury_category" required state={state} />
            <Field label="Body region" name="body_region" required state={state} />
            <SelectField
              label="Side"
              name="side"
              required
              state={state}
              options={[
                ["left", "Left"],
                ["right", "Right"],
                ["bilateral", "Bilateral"],
                ["not_applicable", "Not applicable"],
              ]}
            />
            <Field label="Date of injury" name="date_of_injury" type="date" required state={state} />
            <SelectField
              label="Return plan template"
              name="template_id"
              required
              state={state}
              options={templates.map((template) => [
                template.id,
                `${template.name} (${template.injury_category})`,
              ])}
            />
            <div className="sm:col-span-2">
              <Field label="Clinical summary" name="summary" multiline state={state} />
            </div>
          </div>
        </div>
      </section>

      <div className="mx-auto flex w-full max-w-7xl justify-end px-4 pb-8 sm:px-6 lg:px-8">
        <SubmitButton />
      </div>
    </form>
  );
}

function Field({
  label,
  name,
  state,
  type = "text",
  required = false,
  multiline = false,
}: {
  label: string;
  name: string;
  state: CaseCreationActionState;
  type?: string;
  required?: boolean;
  multiline?: boolean;
}) {
  const error = state.fieldErrors[name];
  const className =
    "mt-1 w-full border border-mist bg-white px-3 py-2 text-sm text-ink outline-none focus:border-pine focus:ring-2 focus:ring-pine/20";

  return (
    <label className="block text-sm font-medium text-ink">
      {label}
      {multiline ? (
        <textarea className={`${className} min-h-24 resize-y`} name={name} aria-invalid={Boolean(error)} />
      ) : (
        <input className={className} name={name} type={type} required={required} aria-invalid={Boolean(error)} />
      )}
      {error ? <span className="mt-1 block text-xs font-semibold text-rust">{error}</span> : null}
    </label>
  );
}

function SelectField({
  label,
  name,
  state,
  options,
  required = false,
}: {
  label: string;
  name: string;
  state: CaseCreationActionState;
  options: Array<[string, string]>;
  required?: boolean;
}) {
  const error = state.fieldErrors[name];
  return (
    <label className="block text-sm font-medium text-ink">
      {label}
      <select
        aria-invalid={Boolean(error)}
        className="mt-1 w-full border border-mist bg-white px-3 py-2 text-sm text-ink outline-none focus:border-pine focus:ring-2 focus:ring-pine/20"
        name={name}
        required={required}
      >
        <option value="">Select</option>
        {options.map(([value, text]) => (
          <option key={value} value={value}>
            {text}
          </option>
        ))}
      </select>
      {error ? <span className="mt-1 block text-xs font-semibold text-rust">{error}</span> : null}
    </label>
  );
}

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button
      className="inline-flex min-h-11 items-center justify-center bg-pine px-5 text-sm font-semibold text-white shadow-panel disabled:cursor-not-allowed disabled:opacity-60"
      disabled={pending}
      type="submit"
    >
      {pending ? "Creating..." : "Create case"}
    </button>
  );
}
