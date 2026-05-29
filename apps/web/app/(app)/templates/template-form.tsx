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
    <form action={formAction} className="grid gap-6" noValidate>
      {template ? <input name="template_id" type="hidden" value={template.id} /> : null}
      {state.status === "error" ? (
        <div className="border border-rust/30 bg-rust/10 px-4 py-3 text-sm text-rust" role="alert">
          {state.message}
        </div>
      ) : null}

      <section className="border-y border-mist bg-white">
        <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[280px_1fr] lg:px-8">
          <div>
            <h2 className="text-lg font-semibold text-ink">Template profile</h2>
            <p className="mt-1 text-sm text-slate-600">Name the staged plan and match it to an injury category.</p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Template name" name="name" defaultValue={template?.name ?? ""} required state={state} />
            <Field
              label="Injury category"
              name="injury_category"
              defaultValue={template?.injury_category ?? ""}
              required
              state={state}
            />
            <div className="sm:col-span-2">
              <Field
                label="Description"
                name="description"
                defaultValue={template?.description ?? ""}
                multiline
                state={state}
              />
            </div>
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

      <div className="mx-auto flex w-full max-w-7xl justify-end px-4 pb-8 sm:px-6 lg:px-8">
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
    <section className="border-y border-mist bg-white">
      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[280px_1fr] lg:px-8">
        <div>
          <h2 className="text-lg font-semibold text-ink">Phase {index}</h2>
          <p className="mt-1 text-sm text-slate-600">
            {required ? "First phase and milestone are required." : "Optional second phase for staged progression."}
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
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
          <div className="sm:col-span-2">
            <Field
              label={`Phase ${index} milestone instructions`}
              name={`${prefix}_milestone_instructions`}
              defaultValue={milestone?.instructions ?? ""}
              multiline
              state={state}
            />
          </div>
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
  const className =
    "mt-1 w-full border border-mist bg-white px-3 py-2 text-sm text-ink outline-none focus:border-pine focus:ring-2 focus:ring-pine/20";

  return (
    <label className="block text-sm font-medium text-ink">
      {label}
      {multiline ? (
        <textarea
          aria-invalid={Boolean(error)}
          className={`${className} min-h-24 resize-y`}
          defaultValue={defaultValue}
          name={name}
        />
      ) : (
        <input
          aria-invalid={Boolean(error)}
          className={className}
          defaultValue={defaultValue}
          name={name}
          required={required}
          type={type}
        />
      )}
      {error ? <span className="mt-1 block text-xs font-semibold text-rust">{error}</span> : null}
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
    <label className="block text-sm font-medium text-ink">
      {label}
      <select
        className="mt-1 w-full border border-mist bg-white px-3 py-2 text-sm text-ink outline-none focus:border-pine focus:ring-2 focus:ring-pine/20"
        defaultValue={defaultValue}
        name={name}
      >
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
      className="inline-flex min-h-11 items-center justify-center bg-pine px-5 text-sm font-semibold text-white shadow-panel disabled:cursor-not-allowed disabled:opacity-60"
      disabled={pending}
      type="submit"
    >
      {pending ? "Saving..." : label}
    </button>
  );
}
