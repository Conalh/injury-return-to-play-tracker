import { expect, test } from "@playwright/test";

test("limited share page hides clinical detail while showing participation status", async ({ page }) => {
  await page.goto("/share/demo-coach-token");

  await expect(page.getByRole("heading", { name: "Riley Chen" })).toBeVisible();
  await expect(page.getByText("Coach status view")).toBeVisible();
  await expect(page.getByText("Modified training only")).toBeVisible();
  await expect(page.getByText("No contact drills. No full-speed cutting.")).toBeVisible();
  await expect(page.getByText("Clearance decision required.")).toBeVisible();

  await expect(page.getByText("Symptom trend")).toHaveCount(0);
  await expect(page.getByText("Pain 5")).toHaveCount(0);
  await expect(page.getByText("guardian@example.com")).toHaveCount(0);
});
