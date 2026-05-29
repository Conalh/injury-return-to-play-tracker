"use client";

import { useActionState } from "react";
import { useFormStatus } from "react-dom";
import type { ApiAthlete } from "@/lib/api-client";
import { type AthleteEditActionState, updateAthleteAction } from "./actions";

const initialAthleteEditState: AthleteEditActionState = {
  status: "idle",
  message: "",
  fieldErrors: {},
};

export function AthleteEditForm({ athlete }: { athlete: ApiAthlete }) {
  const [state, formAction] = useActionState<AthleteEditActionState, FormData>(
    updateAthleteAction,
    initialAthleteEditState,
  );

  return (
    <form action={formAction} className="rp-form" noValidate>
      <input name="athlete_id" type="hidden" value={athlete.id} />
      <section className="rp-form-section">
        <div className="rp-form-section-intro">
          <h2>Athlete profile</h2>
          <p>Update fields used by clinician workflows and family sharing.</p>
        </div>
        <div className="rp-form-fields rp-form-fields-2">
          {state.status === "error" ? (
            <div className="rp-form-error rp-form-grid-full" role="alert">
              {state.message}
            </div>
          ) : null}
          <Field label="Athlete name" name="name" defaultValue={athlete.name} required state={state} />
          <Field
            label="Date of birth"
            name="date_of_birth"
            defaultValue={athlete.date_of_birth}
            required
            state={state}
            type="date"
          />
          <Field label="Sport" name="sport" defaultValue={athlete.sport} required state={state} />
          <Field label="Position" name="position" defaultValue={athlete.position ?? ""} state={state} />
          <Field
            label="Guardian email"
            name="guardian_contact"
            defaultValue={athlete.guardian_contact ?? ""}
            state={state}
            type="email"
          />
          <label className="rp-field-checkbox">
            <input defaultChecked={athlete.active} name="active" type="checkbox" />
            Active athlete
          </label>
          <div className="rp-form-grid-full">
            <SubmitButton />
          </div>
        </div>
      </section>
    </form>
  );
}

function Field({
  label,
  name,
  state,
  defaultValue,
  type = "text",
  required = false,
}: {
  label: string;
  name: string;
  state: AthleteEditActionState;
  defaultValue: string;
  type?: string;
  required?: boolean;
}) {
  const error = state.fieldErrors[name];
  return (
    <label className="rp-field">
      {label}
      <input
        aria-invalid={Boolean(error)}
        defaultValue={defaultValue}
        name={name}
        required={required}
        type={type}
      />
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
      {pending ? "Saving..." : "Save athlete"}
    </button>
  );
}
