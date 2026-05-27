import { expect, test } from "@playwright/test";

test("athlete portal accepts symptom check-in without clinician-only detail", async ({ page }) => {
  const athleteName = `Portal Athlete ${Date.now()}`;

  await page.goto("/cases/new");

  await page.getByLabel("Athlete name").fill(athleteName);
  await page.getByLabel("Date of birth").fill("2009-06-04");
  await page.getByLabel("Sport").fill("Soccer");
  await page.getByLabel("Position").fill("Midfielder");
  await page.getByLabel("Guardian email").fill("guardian@example.com");

  await page.getByLabel("Case title").fill("Left ankle sprain");
  await page.getByLabel("Injury category").fill("sprain");
  await page.getByLabel("Body region").fill("ankle");
  await page.getByLabel("Side").selectOption("left");
  await page.getByLabel("Date of injury").fill("2026-05-24");
  await page.getByLabel("Clinical summary").fill("Athlete portal browser test.");
  await page.getByLabel("Return plan template").selectOption({ index: 1 });
  await page.getByRole("button", { name: "Create case" }).click();

  await expect(page).toHaveURL(/\/cases\/case_/);
  await page.getByRole("button", { name: "Create share link" }).click();
  await page.getByLabel("Audience").selectOption("athlete");
  await page.getByLabel("Allowed activities").fill("Assigned rehab and walking drills.");
  await page.getByLabel("Restricted activities").fill("No sprinting or contact drills.");
  await page.getByLabel("Next review date").fill("2026-05-30");
  await page.getByLabel("Share note").fill("Today: complete rehab set and report symptoms.");
  await page.getByRole("button", { name: "Create limited link" }).click();
  const shareUrl = await page.getByLabel("Share URL").inputValue();

  await page.goto(shareUrl);
  await expect(page.getByText("Athlete portal")).toBeVisible();
  await expect(page.getByRole("heading", { name: athleteName })).toBeVisible();
  await expect(page.getByText("Current phase")).toBeVisible();
  await expect(page.getByText("Assigned activities")).toBeVisible();
  await expect(page.getByText("Today's instructions")).toBeVisible();
  await expect(page.getByText("Clinician message")).toBeVisible();
  await expect(page.getByText("This is not medical clearance.")).toBeVisible();

  await page.getByLabel("Pain score").fill("3");
  await page.getByLabel("Swelling").selectOption("mild");
  await page.getByLabel("Confidence").fill("4");
  await page.getByLabel("Symptom notes").fill("Felt steady after rehab.");
  await page.getByRole("button", { name: "Submit symptom check-in" }).click();

  await expect(page.getByText("Symptom check-in received.")).toBeVisible();
  await expect(page.getByText("Symptom trend")).toHaveCount(0);
  await expect(page.getByText("Functional tests")).toHaveCount(0);
  await expect(page.getByText("guardian@example.com")).toHaveCount(0);
});
