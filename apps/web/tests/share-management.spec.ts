import { expect, test } from "@playwright/test";

test("clinician creates and revokes a limited coach share link from case detail", async ({ page }) => {
  const athleteName = `Share Athlete ${Date.now()}`;

  await page.goto("/cases/new");

  await page.getByLabel("Athlete name").fill(athleteName);
  await page.getByLabel("Date of birth").fill("2009-03-12");
  await page.getByLabel("Sport").fill("Soccer");
  await page.getByLabel("Position").fill("Defender");
  await page.getByLabel("Guardian email").fill("guardian@example.com");

  await page.getByLabel("Case title").fill("Right hamstring strain");
  await page.getByLabel("Injury category").fill("strain");
  await page.getByLabel("Body region").fill("hamstring");
  await page.getByLabel("Side").selectOption("right");
  await page.getByLabel("Date of injury").fill("2026-05-23");
  await page.getByLabel("Clinical summary").fill("Share management browser test.");
  await page.getByLabel("Return plan template").selectOption({ index: 1 });
  await page.getByRole("button", { name: "Create case" }).click();

  await expect(page).toHaveURL(/\/cases\/case_/);
  await expect(page.getByRole("heading", { name: athleteName })).toBeVisible();

  await page.getByRole("button", { name: "Create share link" }).click();
  await expect(page.getByRole("dialog", { name: "Create limited share link" })).toBeVisible();
  await page.getByLabel("Audience").selectOption("coach");
  await page.getByLabel("Allowed activities").fill("Non-contact practice and assigned rehab work.");
  await page.getByLabel("Restricted activities").fill("No sprinting or contact drills.");
  await page.getByLabel("Expires in days").fill("5");
  await page.getByLabel("Next review date").fill("2026-05-30");
  await page.getByLabel("Share note").fill("Review after weekend symptom check.");
  await page.getByRole("button", { name: "Create limited link" }).click();

  await expect(page.getByLabel("Share URL")).toBeVisible();
  await expect(page.getByRole("button", { name: "Copy link" })).toBeVisible();
  await expect(page.getByText("share_created")).toBeVisible();
  const shareUrl = await page.getByLabel("Share URL").inputValue();
  const managementUrl = page.url();

  await page.goto(shareUrl);
  await expect(page.getByRole("heading", { name: athleteName })).toBeVisible();
  await expect(page.getByText("No sprinting or contact drills.")).toBeVisible();
  await expect(page.getByText("Symptom trend")).toHaveCount(0);
  await expect(page.getByText("guardian@example.com")).toHaveCount(0);

  await page.goto(managementUrl);
  await page.getByRole("button", { name: "Revoke link" }).click();

  await expect(page.getByText("share_revoked")).toBeVisible();
  await page.goto(shareUrl);
  await expect(page.getByRole("heading", { name: "Share unavailable" })).toBeVisible();
});
