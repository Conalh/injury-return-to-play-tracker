"use server";

import { redirect } from "next/navigation";
import {
  createClearanceDecision,
  currentActorId,
  currentActorRole,
} from "@/lib/api-client";
import { formValue, optionalFormValue } from "@/lib/form-data";

export async function recordClearanceDecisionAction(formData: FormData): Promise<void> {
  const caseId = formValue(formData, "case_id");
  await createClearanceDecision(caseId, {
    injury_case_id: caseId,
    phase_id: formValue(formData, "phase_id"),
    decision: formValue(formData, "decision") as
      | "advance"
      | "hold"
      | "clear_full"
      | "close_case",
    decided_by: currentActorId(),
    decided_by_role: currentActorRole(),
    rationale: formValue(formData, "rationale"),
    restrictions: optionalFormValue(formData, "restrictions"),
  });
  redirect(`/cases/${caseId}`);
}
