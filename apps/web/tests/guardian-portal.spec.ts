import { expect, test } from "@playwright/test";

test("guardian portal shows conservative status and records acknowledgment", async ({ page }) => {
  const athleteName = `Guardian Athlete ${Date.now()}`;

  await page.goto("/cases/new");

  await page.getByLabel("Athlete name").fill(athleteName);
  await page.getByLabel("Date of birth").fill("2008-09-10");
  await page.getByLabel("Sport").fill("Soccer");
  await page.getByLabel("Position").fill("Goalkeeper");
  await page.getByLabel("Guardian email").fill("guardian@example.com");

  await page.getByLabel("Case title").fill("Right knee soreness");
  await page.getByLabel("Injury category").fill("soreness");
  await page.getByLabel("Body region").fill("knee");
  await page.getByLabel("Side").selectOption("right");
  await page.getByLabel("Date of injury").fill("2026-05-25");
  await page.getByLabel("Clinical summary").fill("Guardian portal browser test.");
  await page.getByLabel("Return plan template").selectOption({ index: 1 });
  await page.getByRole("button", { name: "Create case" }).click();

  await expect(page).toHaveURL(/\/cases\/case_/);
  await page.getByRole("button", { name: "Create share link" }).click();
  await page.getByLabel("Audience").selectOption("guardian");
  await page.getByLabel("Allowed activities").fill("Rehab work and walking drills.");
  await page.getByLabel("Restricted activities").fill("No practice or games.");
  await page.getByLabel("Next review date").fill("2026-05-31");
  await page.getByLabel("Share note").fill("Please monitor participation restrictions.");
  await page.getByRole("button", { name: "Create limited link" }).click();
  const shareUrl = await page.getByLabel("Share URL").inputValue();

  await page.goto(shareUrl);
  await expect(page.getByText("Guardian portal")).toBeVisible();
  await expect(page.getByRole("heading", { name: athleteName })).toBeVisible();
  await expect(page.getByText("Participation status")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Restrictions" })).toBeVisible();
  await expect(page.getByText("Next review")).toBeVisible();
  await expect(page.getByText("Clinician note")).toBeVisible();
  await expect(page.getByText("Rehab work and walking drills.")).toBeVisible();
  await expect(page.getByText("No practice or games.")).toBeVisible();
  await expect(page.getByText("Symptom trend")).toHaveCount(0);
  await expect(page.getByText("Functional tests")).toHaveCount(0);
  await expect(page.getByText("Pain score")).toHaveCount(0);
  await expect(page.getByText("guardian@example.com")).toHaveCount(0);

  await page.getByLabel("Guardian name").fill("Riley Guardian");
  await page.getByLabel("Relationship").fill("Parent");
  await page.getByLabel("Acknowledgment note").fill("I understand the current restrictions.");
  await page.getByRole("button", { name: "Record acknowledgment" }).click();

  await expect(page.getByText("Guardian acknowledgment recorded.")).toBeVisible();
});
