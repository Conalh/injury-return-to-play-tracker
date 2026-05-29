"use server";

import { redirect } from "next/navigation";
import {
  createShareToken,
  currentActorId,
  revokeShareToken,
} from "@/lib/api-client";

export async function createShareLinkAction(formData: FormData): Promise<void> {
  const caseId = formValue(formData, "case_id");
  const share = await createShareToken(caseId, {
    injury_case_id: caseId,
    audience: formValue(formData, "audience") as "coach" | "guardian" | "athlete",
    expires_in_days: Number(formValue(formData, "expires_in_days") || "7"),
    created_by: currentActorId(),
    allowed_activities: formValue(formData, "allowed_activities"),
    restricted_activities: formValue(formData, "restricted_activities"),
    clinician_note: formValue(formData, "clinician_note"),
    next_review_date: optionalFormValue(formData, "next_review_date"),
  });

  redirect(
    `/cases/${caseId}?share_token=${encodeURIComponent(share.token)}&share_audience=${share.audience}`,
  );
}

export async function revokeShareLinkAction(formData: FormData): Promise<void> {
  const caseId = formValue(formData, "case_id");
  await revokeShareToken(formValue(formData, "share_token"));
  redirect(`/cases/${caseId}?share_revoked=1`);
}

function formValue(formData: FormData, key: string): string {
  const value = formData.get(key);
  return typeof value === "string" ? value.trim() : "";
}

function optionalFormValue(formData: FormData, key: string): string | null {
  const value = formValue(formData, key);
  return value || null;
}
