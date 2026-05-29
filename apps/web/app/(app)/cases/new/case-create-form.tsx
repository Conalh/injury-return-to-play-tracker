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
    <form action={formAction} className="rp-form" noValidate>
      {state.status === "error" ? (
        <p className="rp-form-error" role="alert">
          {state.message}
        </p>
      ) : null}

      <section className="rp-form-section">
        <div className="rp-form-section-intro">
          <UserPlus aria-hidden="true" className="h-5 w-5" />
          <h2>Athlete profile</h2>
          <p>Create the athlete record used for this return-to-play case.</p>
        </div>
        <div className="rp-form-fields rp-form-fields-2">
          <Field label="Athlete name" name="athlete_name" required state={state} />
          <Field label="Date of birth" name="date_of_birth" type="date" required state={state} />
          <Field label="Sport" name="sport" required state={state} />
          <Field label="Position" name="position" state={state} />
          <Field label="Guardian email" name="guardian_contact" type="email" state={state} />
        </div>
      </section>

      <section className="rp-form-section">
        <div className="rp-form-section-intro">
          <CheckCircle2 aria-hidden="true" className="h-5 w-5" />
          <h2>Case and template</h2>
          <p>Open the injury case and apply the initial staged plan.</p>
        </div>
        <div className="rp-form-fields rp-form-fields-2">
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
          <div className="rp-form-grid-full">
            <Field label="Clinical summary" name="summary" multiline state={state} />
          </div>
        </div>
      </section>

      <div className="rp-form-actions">
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

  return (
    <label className="rp-field">
      {label}
      {multiline ? (
        <textarea aria-invalid={Boolean(error)} name={name} />
      ) : (
        <input aria-invalid={Boolean(error)} name={name} required={required} type={type} />
      )}
      {error ? <span className="rp-field-error">{error}</span> : null}
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
    <label className="rp-field">
      {label}
      <select aria-invalid={Boolean(error)} name={name} required={required}>
        <option value="">Select</option>
        {options.map(([value, text]) => (
          <option key={value} value={value}>
            {text}
          </option>
        ))}
      </select>
      {error ? <span className="rp-field-error">{error}</span> : null}
    </label>
  );
}

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button
      className="rp-primary-button disabled:cursor-not-allowed disabled:opacity-60"
      disabled={pending}
      type="submit"
    >
      {pending ? "Creating..." : "Create case"}
    </button>
  );
}
