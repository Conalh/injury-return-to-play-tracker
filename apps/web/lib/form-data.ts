export function formValue(formData: FormData, key: string): string {
  const value = formData.get(key);
  return typeof value === "string" ? value.trim() : "";
}

export function optionalFormValue(formData: FormData, key: string): string | null {
  const value = formValue(formData, key);
  return value || null;
}

export function optionalNumberFormValue(formData: FormData, key: string): number | null {
  const value = formValue(formData, key);
  return value ? Number(value) : null;
}

export function requiredFieldErrors(
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
