"use server";

import { redirect } from "next/navigation";
import {
  archiveTemplate,
  createTemplate,
  currentActorId,
  currentOrganizationId,
  updateTemplateVersion,
  UnauthorizedApiError,
  type TemplatePayload,
} from "@/lib/api-client";
import { formValue, optionalFormValue, requiredFieldErrors } from "@/lib/form-data";

export type TemplateActionState = {
  status: "idle" | "error";
  message: string;
  fieldErrors: Record<string, string>;
};

export async function createTemplateAction(
  _previousState: TemplateActionState,
  formData: FormData,
): Promise<TemplateActionState> {
  const parsed = parseTemplateForm(formData);
  if (Object.keys(parsed.fieldErrors).length > 0) {
    return {
      status: "error",
      message: "Please complete the required template fields.",
      fieldErrors: parsed.fieldErrors,
    };
  }

  try {
    await createTemplate(parsed.payload);
  } catch (error) {
    return templateError(error, "The template could not be saved. Review the fields and try again.");
  }
  redirect("/templates");
}

export async function updateTemplateAction(
  _previousState: TemplateActionState,
  formData: FormData,
): Promise<TemplateActionState> {
  const templateId = formValue(formData, "template_id");
  const parsed = parseTemplateForm(formData);
  if (!templateId) {
    parsed.fieldErrors.template_id = "Required";
  }
  if (Object.keys(parsed.fieldErrors).length > 0) {
    return {
      status: "error",
      message: "Please complete the required template fields.",
      fieldErrors: parsed.fieldErrors,
    };
  }

  try {
    await updateTemplateVersion(templateId, parsed.payload);
  } catch (error) {
    return templateError(error, "The template version could not be saved. Review the fields and try again.");
  }
  redirect("/templates");
}

export async function archiveTemplateAction(formData: FormData): Promise<void> {
  const templateId = formValue(formData, "template_id");
  const templateName = formValue(formData, "template_name");
  await archiveTemplate(templateId);
  redirect(`/templates?archived=${encodeURIComponent(templateName)}`);
}

function parseTemplateForm(formData: FormData): {
  payload: TemplatePayload;
  fieldErrors: Record<string, string>;
} {
  const fieldErrors = requiredFieldErrors(formData, [
    "name",
    "injury_category",
    "phase_1_name",
    "phase_1_milestone_title",
  ]);

  const phases = [1, 2]
    .map((index) => phaseFromForm(formData, index, fieldErrors))
    .filter((phase): phase is TemplatePayload["phases"][number] => phase !== null);

  return {
    fieldErrors,
    payload: {
      organization_id: currentOrganizationId(),
      name: formValue(formData, "name"),
      injury_category: formValue(formData, "injury_category"),
      description: optionalFormValue(formData, "description"),
      created_by: currentActorId(),
      phases,
    },
  };
}

function phaseFromForm(
  formData: FormData,
  index: number,
  fieldErrors: Record<string, string>,
): TemplatePayload["phases"][number] | null {
  const prefix = `phase_${index}`;
  const name = formValue(formData, `${prefix}_name`);
  const milestoneTitle = formValue(formData, `${prefix}_milestone_title`);
  if (index > 1 && !name && !milestoneTitle) {
    return null;
  }
  if (!name) {
    fieldErrors[`${prefix}_name`] = "Required";
  }
  if (!milestoneTitle) {
    fieldErrors[`${prefix}_milestone_title`] = "Required";
  }

  return {
    name,
    order_index: index - 1,
    objective: optionalFormValue(formData, `${prefix}_objective`),
    minimum_days: Number(formValue(formData, `${prefix}_minimum_days`) || "0"),
    exit_summary: optionalFormValue(formData, `${prefix}_exit_summary`),
    milestones: [
      {
        title: milestoneTitle,
        kind: formValue(formData, `${prefix}_milestone_kind`) || "other",
        required: formData.get(`${prefix}_milestone_required`) !== "off",
        instructions: optionalFormValue(formData, `${prefix}_milestone_instructions`),
      },
    ],
  };
}

function templateError(error: unknown, fallback: string): TemplateActionState {
  if (error instanceof UnauthorizedApiError) {
    return {
      status: "error",
      message: "Your session is not allowed to manage templates.",
      fieldErrors: {},
    };
  }
  return { status: "error", message: fallback, fieldErrors: {} };
}
