"use server";

import { redirect } from "next/navigation";
import {
  submitAthleteSymptomCheckIn,
  submitGuardianAcknowledgment,
} from "@/lib/api-client";
import { formValue, optionalFormValue } from "@/lib/form-data";

export async function submitAthleteSymptomCheckInAction(formData: FormData): Promise<void> {
  const token = formValue(formData, "token");
  await submitAthleteSymptomCheckIn(token, {
    date: new Date().toISOString().slice(0, 10),
    pain: Number(formValue(formData, "pain")),
    swelling: formValue(formData, "swelling") as "none" | "mild" | "moderate" | "severe",
    confidence: Number(formValue(formData, "confidence")),
    notes: optionalFormValue(formData, "notes"),
  });
  redirect(`/share/${token}?checkin=received`);
}

export async function submitGuardianAcknowledgmentAction(formData: FormData): Promise<void> {
  const token = formValue(formData, "token");
  await submitGuardianAcknowledgment(token, {
    acknowledged_by: formValue(formData, "acknowledged_by"),
    relationship: formValue(formData, "relationship"),
    message: optionalFormValue(formData, "message"),
  });
  redirect(`/share/${token}?acknowledgment=recorded`);
}
