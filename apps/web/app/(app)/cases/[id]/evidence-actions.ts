"use server";

import { redirect } from "next/navigation";
import {
  createFunctionalTest,
  createSymptomLog,
  createWorkloadSession,
  currentActorId,
  updateMilestoneEvidence,
} from "@/lib/api-client";
import {
  formValue,
  optionalFormValue,
  optionalNumberFormValue,
} from "@/lib/form-data";

export async function recordSymptomAction(formData: FormData): Promise<void> {
  const caseId = formValue(formData, "case_id");
  await createSymptomLog(caseId, {
    injury_case_id: caseId,
    athlete_id: formValue(formData, "athlete_id"),
    date: formValue(formData, "symptom_date"),
    pain: Number(formValue(formData, "pain")),
    swelling: formValue(formData, "swelling"),
    confidence: Number(formValue(formData, "confidence")),
    notes: optionalFormValue(formData, "symptom_notes"),
  });
  redirect(`/cases/${caseId}`);
}

export async function recordFunctionalTestAction(formData: FormData): Promise<void> {
  const caseId = formValue(formData, "case_id");
  await createFunctionalTest(caseId, {
    injury_case_id: caseId,
    name: formValue(formData, "functional_test_name"),
    test_date: formValue(formData, "test_date"),
    result_value: optionalNumberFormValue(formData, "result_value"),
    unit: optionalFormValue(formData, "unit"),
    side_to_side_difference_percent: optionalNumberFormValue(formData, "side_difference"),
    passed: formValue(formData, "passed") === "true",
    recorded_by: currentActorId(),
    notes: optionalFormValue(formData, "functional_test_notes"),
  });
  redirect(`/cases/${caseId}`);
}

export async function recordWorkloadAction(formData: FormData): Promise<void> {
  const caseId = formValue(formData, "case_id");
  await createWorkloadSession(caseId, {
    injury_case_id: caseId,
    date: formValue(formData, "workload_date"),
    activity: formValue(formData, "activity"),
    duration_minutes: Number(formValue(formData, "duration_minutes")),
    intensity: Number(formValue(formData, "intensity")),
    completed: formValue(formData, "completed") === "true",
    symptom_response: optionalFormValue(formData, "symptom_response"),
    notes: optionalFormValue(formData, "workload_notes"),
  });
  redirect(`/cases/${caseId}`);
}

export async function attachMilestoneEvidenceAction(formData: FormData): Promise<void> {
  const caseId = formValue(formData, "case_id");
  await updateMilestoneEvidence(caseId, formValue(formData, "milestone_id"), {
    status: formValue(formData, "milestone_status") as "not_started" | "passed" | "failed" | "waived",
    recorded_by: currentActorId(),
    notes: optionalFormValue(formData, "milestone_notes"),
    evidence_json: {
      source: formValue(formData, "evidence_source"),
    },
  });
  redirect(`/cases/${caseId}`);
}
