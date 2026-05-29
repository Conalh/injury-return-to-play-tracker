"use client";

import { useActionState } from "react";
import { useFormStatus } from "react-dom";
import type { ApiTemplateDetail } from "@/lib/api-client";
import {
  createTemplateAction,
  type TemplateActionState,
  updateTemplateAction,
} from "./actions";

const initialTemplateState: TemplateActionState = {
  status: "idle",
  message: "",
  fieldErrors: {},
};

const milestoneKinds = [
  ["symptom", "Symptom"],
  ["function", "Function"],
  ["strength", "Strength"],
  ["range_of_motion", "Range of motion"],
  ["workload", "Workload"],
  ["clinician_review", "Clinician review"],
  ["other", "Other"],
];

export function TemplateForm({ template }: { template?: ApiTemplateDetail }) {
  const action = template ? updateTemplateAction : createTemplateAction;
  const [state, formAction] = useActionState<TemplateActionState, FormData>(
    action,
    initialTemplateState,
  );
  const phases = template?.phases ?? [];

  return (
    <form action={formAction} className="rp-form" noValidate>
      {template ? <input name="template_id" type="hidden" value={template.id} /> : null}
      {state.status === "error" ? (
        <p className="rp-form-error" role="alert">
          {state.message}
        </p>
      ) : null}

      <section className="rp-form-section">
        <div className="rp-form-section-intro">
          <h2>Template profile</h2>
          <p>Name the staged plan and match it to an injury category.</p>
        </div>
        <div className="rp-form-fields rp-form-fields-2">
          <Field label="Template name" name="name" defaultValue={template?.name ?? ""} required state={state} />
          <Field
            label="Injury category"
            name="injury_category"
            defaultValue={template?.injury_category ?? ""}
            required
            state={state}
          />
          <div className="rp-form-grid-full">
            <Field
              label="Description"
              name="description"
              defaultValue={template?.description ?? ""}
              multiline
              state={state}
            />
          </div>
        </div>
      </section>

      {[1, 2].map((index) => (
        <PhaseEditor
          key={index}
          index={index}
          phase={phases[index - 1]}
          required={index === 1}
          state={state}
        />
      ))}

      <div className="rp-form-actions">
        <SubmitButton label={template ? "Save new version" : "Save template"} />
      </div>
    </form>
  );
}

function PhaseEditor({
  index,
  phase,
  state,
  required,
}: {
  index: number;
  phase?: ApiTemplateDetail["phases"][number];
  state: TemplateActionState;
  required: boolean;
}) {
  const prefix = `phase_${index}`;
  const milestone = phase?.milestones[0];
  return (
    <section className="rp-form-section">
      <div className="rp-form-section-intro">
        <h2>Phase {index}</h2>
        <p>
          {required ? "First phase and milestone are required." : "Optional second phase for staged progression."}
        </p>
      </div>
      <div className="rp-form-fields rp-form-fields-2">
          <Field
            label={`Phase ${index} name`}
            name={`${prefix}_name`}
            defaultValue={phase?.name ?? ""}
            required={required}
            state={state}
          />
          <Field
            label={`Phase ${index} minimum days`}
            name={`${prefix}_minimum_days`}
            defaultValue={String(phase?.minimum_days ?? 0)}
            state={state}
            type="number"
          />
          <Field
            label={`Phase ${index} objective`}
            name={`${prefix}_objective`}
            defaultValue={phase?.objective ?? ""}
            state={state}
          />
          <Field
            label={`Phase ${index} exit summary`}
            name={`${prefix}_exit_summary`}
            defaultValue={phase?.exit_summary ?? ""}
            state={state}
          />
          <Field
            label={`Phase ${index} milestone title`}
            name={`${prefix}_milestone_title`}
            defaultValue={milestone?.title ?? ""}
            required={required}
            state={state}
          />
          <SelectField
            label={`Phase ${index} milestone kind`}
            name={`${prefix}_milestone_kind`}
            defaultValue={milestone?.kind ?? "other"}
            options={milestoneKinds}
          />
          <div className="rp-form-grid-full">
            <Field
              label={`Phase ${index} milestone instructions`}
              name={`${prefix}_milestone_instructions`}
              defaultValue={milestone?.instructions ?? ""}
              multiline
              state={state}
            />
          </div>
      </div>
    </section>
  );
}

function Field({
  label,
  name,
  state,
  defaultValue,
  type = "text",
  required = false,
  multiline = false,
}: {
  label: string;
  name: string;
  state: TemplateActionState;
  defaultValue: string;
  type?: string;
  required?: boolean;
  multiline?: boolean;
}) {
  const error = state.fieldErrors[name];

  return (
    <label className="rp-field">
      {label}
      {multiline ? (
        <textarea aria-invalid={Boolean(error)} defaultValue={defaultValue} name={name} />
      ) : (
        <input
          aria-invalid={Boolean(error)}
          defaultValue={defaultValue}
          name={name}
          required={required}
          type={type}
        />
      )}
      {error ? <span className="rp-field-error">{error}</span> : null}
    </label>
  );
}

function SelectField({
  label,
  name,
  defaultValue,
  options,
}: {
  label: string;
  name: string;
  defaultValue: string;
  options: string[][];
}) {
  return (
    <label className="rp-field">
      {label}
      <select defaultValue={defaultValue} name={name}>
        {options.map(([value, text]) => (
          <option key={value} value={value}>
            {text}
          </option>
        ))}
      </select>
    </label>
  );
}

function SubmitButton({ label }: { label: string }) {
  const { pending } = useFormStatus();
  return (
    <button
      className="rp-primary-button disabled:cursor-not-allowed disabled:opacity-60"
      disabled={pending}
      type="submit"
    >
      {pending ? "Saving..." : label}
    </button>
  );
}
