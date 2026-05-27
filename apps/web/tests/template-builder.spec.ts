import { expect, test } from "@playwright/test";

test("clinician creates a staged template and applies it to a new case", async ({ page }) => {
  const templateName = `Hamstring staged return ${Date.now()}`;
  const athleteName = `Template Runner ${Date.now()}`;

  await page.goto("/templates");
  await expect(page.getByRole("heading", { name: "Template builder" })).toBeVisible();

  await page.getByRole("link", { name: "New template" }).click();
  await page.getByLabel("Template name").fill(templateName);
  await page.getByLabel("Injury category").fill("hamstring");
  await page.getByLabel("Description").fill("Hamstring progression for field athletes.");
  await page.getByLabel("Phase 1 name").fill("Restore stride");
  await page.getByLabel("Phase 1 objective").fill("Jog without symptom increase.");
  await page.getByLabel("Phase 1 minimum days").fill("2");
  await page.getByLabel("Phase 1 milestone title").fill("Pain-free jog");
  await page.getByLabel("Phase 1 milestone kind").selectOption("function");
  await page.getByLabel("Phase 2 name").fill("Controlled sprint");
  await page.getByLabel("Phase 2 objective").fill("Accelerate under control.");
  await page.getByLabel("Phase 2 minimum days").fill("3");
  await page.getByLabel("Phase 2 milestone title").fill("Complete controlled sprint");
  await page.getByLabel("Phase 2 milestone kind").selectOption("workload");
  await page.getByRole("button", { name: "Save template" }).click();

  await expect(page).toHaveURL(/\/templates$/);
  await expect(page.getByRole("link", { name: new RegExp(templateName) })).toBeVisible();

  await page.goto("/cases/new");
  await page.getByLabel("Athlete name").fill(athleteName);
  await page.getByLabel("Date of birth").fill("2008-08-08");
  await page.getByLabel("Sport").fill("Soccer");
  await page.getByLabel("Position").fill("Forward");
  await page.getByLabel("Case title").fill("Left hamstring strain");
  await page.getByLabel("Injury category").fill("strain");
  await page.getByLabel("Body region").fill("hamstring");
  await page.getByLabel("Side").selectOption("left");
  await page.getByLabel("Date of injury").fill("2026-05-23");
  await page.getByLabel("Return plan template").selectOption({ label: `${templateName} (hamstring)` });
  await page.getByRole("button", { name: "Create case" }).click();

  await expect(page).toHaveURL(/\/cases\/case_/);
  await expect(page.getByRole("heading", { name: athleteName })).toBeVisible();
  await expect(page.getByText("Restore stride")).toBeVisible();
  await expect(page.getByText("Pain-free jog")).toBeVisible();
});

test("clinician edits a template into a new version and archives it", async ({ page }) => {
  const templateName = `Archive candidate ${Date.now()}`;
  const revisedName = `${templateName} revised`;

  await page.goto("/templates/new");
  await page.getByLabel("Template name").fill(templateName);
  await page.getByLabel("Injury category").fill("ankle");
  await page.getByLabel("Phase 1 name").fill("Restore motion");
  await page.getByLabel("Phase 1 milestone title").fill("Motion reviewed");
  await page.getByLabel("Phase 1 milestone kind").selectOption("range_of_motion");
  await page.getByRole("button", { name: "Save template" }).click();

  await page.getByRole("link", { name: new RegExp(templateName) }).click();
  await page.getByLabel("Template name").fill(revisedName);
  await page.getByLabel("Phase 2 name").fill("Non-contact practice");
  await page.getByLabel("Phase 2 milestone title").fill("Practice completed");
  await page.getByLabel("Phase 2 milestone kind").selectOption("workload");
  await page.getByRole("button", { name: "Save new version" }).click();

  await expect(page).toHaveURL(/\/templates$/);
  await expect(page.getByText("v2")).toBeVisible();
  await page.getByRole("button", { name: new RegExp(`Archive ${revisedName}`) }).click();
  await expect(page.getByText(`${revisedName} archived.`)).toBeVisible();
});
