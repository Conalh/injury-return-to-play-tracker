import { expect, test } from "@playwright/test";

test("clinician records named hold and full clearance decisions", async ({ page }) => {
  const athleteName = `Clearance Athlete ${Date.now()}`;

  await page.goto("/cases/new");

  await page.getByLabel("Athlete name").fill(athleteName);
  await page.getByLabel("Date of birth").fill("2008-04-20");
  await page.getByLabel("Sport").fill("Soccer");
  await page.getByLabel("Position").fill("Forward");
  await page.getByLabel("Guardian email").fill("guardian@example.com");

  await page.getByLabel("Case title").fill("Left ankle sprain");
  await page.getByLabel("Injury category").fill("sprain");
  await page.getByLabel("Body region").fill("ankle");
  await page.getByLabel("Side").selectOption("left");
  await page.getByLabel("Date of injury").fill("2026-05-20");
  await page.getByLabel("Clinical summary").fill("Clearance workflow browser test.");
  await page.getByLabel("Return plan template").selectOption({ index: 1 });
  await page.getByRole("button", { name: "Create case" }).click();

  await expect(page).toHaveURL(/\/cases\/case_/);
  await expect(page.getByRole("heading", { name: athleteName })).toBeVisible();
  await expect(page.getByLabel("Rationale")).toHaveAttribute("required", "");

  await page.getByLabel("Decision").selectOption("hold");
  await page.getByLabel("Rationale").fill("Symptoms require another clinician review.");
  await page.getByLabel("Restrictions").fill("No contact drills.");
  await page.getByRole("button", { name: "Record clearance decision" }).click();

  await expect(page.getByText("Symptoms require another clinician review.")).toBeVisible();
  await expect(page.getByText("No contact drills.")).toBeVisible();

  await page.getByLabel("Decision").selectOption("clear_full");
  await page.getByLabel("Rationale").fill("Named clinician cleared full participation.");
  await page.getByLabel("Restrictions").fill("Full unrestricted participation.");
  await page.getByRole("button", { name: "Record clearance decision" }).click();

  await expect(page.getByText("Named clinician cleared full participation.")).toBeVisible();
  await expect(page.getByText("Full unrestricted participation.")).toBeVisible();
});
