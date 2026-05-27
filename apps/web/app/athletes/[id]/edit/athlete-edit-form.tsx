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
    <form action={formAction} className="border-y border-mist bg-white" noValidate>
      <input name="athlete_id" type="hidden" value={athlete.id} />
      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[280px_1fr] lg:px-8">
        <div>
          <h2 className="text-lg font-semibold text-ink">Athlete profile</h2>
          <p className="mt-1 text-sm text-slate-600">Update fields used by clinician workflows and family sharing.</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          {state.status === "error" ? (
            <div className="border border-rust/30 bg-rust/10 px-4 py-3 text-sm text-rust sm:col-span-2" role="alert">
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
          <label className="flex min-h-11 items-center gap-3 text-sm font-medium text-ink">
            <input className="h-4 w-4 accent-pine" defaultChecked={athlete.active} name="active" type="checkbox" />
            Active athlete
          </label>
          <div className="sm:col-span-2">
            <SubmitButton />
          </div>
        </div>
      </div>
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
    <label className="block text-sm font-medium text-ink">
      {label}
      <input
        aria-invalid={Boolean(error)}
        className="mt-1 w-full border border-mist bg-white px-3 py-2 text-sm text-ink outline-none focus:border-pine focus:ring-2 focus:ring-pine/20"
        defaultValue={defaultValue}
        name={name}
        required={required}
        type={type}
      />
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
      {pending ? "Saving..." : "Save athlete"}
    </button>
  );
}
