"use server";

import { redirect } from "next/navigation";
import { updateAthlete, UnauthorizedApiError } from "@/lib/api-client";
import { formValue, optionalFormValue, requiredFieldErrors } from "@/lib/form-data";

export type AthleteEditActionState = {
  status: "idle" | "error";
  message: string;
  fieldErrors: Record<string, string>;
};

export async function updateAthleteAction(
  _previousState: AthleteEditActionState,
  formData: FormData,
): Promise<AthleteEditActionState> {
  const athleteId = formValue(formData, "athlete_id");
  const fieldErrors = requiredFieldErrors(formData, ["name", "date_of_birth", "sport"]);
  if (!athleteId) {
    fieldErrors.athlete_id = "Required";
  }
  if (Object.keys(fieldErrors).length > 0) {
    return {
      status: "error",
      message: "Please complete the required fields before saving.",
      fieldErrors,
    };
  }

  try {
    await updateAthlete(athleteId, {
      name: formValue(formData, "name"),
      date_of_birth: formValue(formData, "date_of_birth"),
      sport: formValue(formData, "sport"),
      position: optionalFormValue(formData, "position"),
      guardian_contact: optionalFormValue(formData, "guardian_contact"),
      active: formData.get("active") === "on",
    });
  } catch (error) {
    if (error instanceof UnauthorizedApiError) {
      return {
        status: "error",
        message: "Your session is not allowed to update athlete profiles.",
        fieldErrors: {},
      };
    }
    return {
      status: "error",
      message: "The athlete profile could not be saved. Review the fields and try again.",
      fieldErrors: {},
    };
  }
  redirect("/cases/new");
}
