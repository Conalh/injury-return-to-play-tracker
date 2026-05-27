"use server";

import { redirect } from "next/navigation";
import {
  applyTemplate,
  createAthlete,
  createInjuryCase,
  currentActorId,
  currentOrganizationId,
  UnauthorizedApiError,
} from "@/lib/api-client";

export type CaseCreationActionState = {
  status: "idle" | "error";
  message: string;
  fieldErrors: Record<string, string>;
};

const REQUIRED_FIELDS = [
  "athlete_name",
  "date_of_birth",
  "sport",
  "case_title",
  "injury_category",
  "body_region",
  "side",
  "date_of_injury",
  "template_id",
] as const;

export async function createCaseAction(
  _previousState: CaseCreationActionState,
  formData: FormData,
): Promise<CaseCreationActionState> {
  const fieldErrors = validateRequiredFields(formData, REQUIRED_FIELDS);
  if (Object.keys(fieldErrors).length > 0) {
    return {
      status: "error",
      message: "Please complete the required fields before creating the case.",
      fieldErrors,
    };
  }

  let createdCaseId: string;
  try {
    const athlete = await createAthlete({
      organization_id: currentOrganizationId(),
      name: formValue(formData, "athlete_name"),
      date_of_birth: formValue(formData, "date_of_birth"),
      sport: formValue(formData, "sport"),
      position: optionalFormValue(formData, "position"),
      guardian_contact: optionalFormValue(formData, "guardian_contact"),
      active: true,
    });
    const injuryCase = await createInjuryCase({
      organization_id: currentOrganizationId(),
      athlete_id: athlete.id,
      title: formValue(formData, "case_title"),
      injury_category: formValue(formData, "injury_category"),
      body_region: formValue(formData, "body_region"),
      side: formValue(formData, "side"),
      date_of_injury: formValue(formData, "date_of_injury"),
      clinician_owner_id: currentActorId(),
      summary: optionalFormValue(formData, "summary"),
    });
    await applyTemplate(injuryCase.id, formValue(formData, "template_id"));
    createdCaseId = injuryCase.id;
  } catch (error) {
    if (error instanceof UnauthorizedApiError) {
      return {
        status: "error",
        message: "Your session is not allowed to create return-to-play cases.",
        fieldErrors: {},
      };
    }
    return {
      status: "error",
      message: "The case could not be created. Review the fields and try again.",
      fieldErrors: {},
    };
  }
  redirect(`/cases/${createdCaseId}`);
}

function validateRequiredFields(
  formData: FormData,
  fields: readonly string[],
): Record<string, string> {
  return fields.reduce<Record<string, string>>((errors, field) => {
    if (!formValue(formData, field)) {
      errors[field] = "Required";
    }
    return errors;
  }, {});
}

function formValue(formData: FormData, key: string): string {
  const value = formData.get(key);
  return typeof value === "string" ? value.trim() : "";
}

function optionalFormValue(formData: FormData, key: string): string | null {
  const value = formValue(formData, key);
  return value || null;
}
