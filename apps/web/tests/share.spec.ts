import { expect, test } from "@playwright/test";

test("limited share page hides clinical detail while showing participation status", async ({ page }) => {
  await page.goto("/share/demo-coach-token");

  await expect(page.getByRole("heading", { name: "Riley Chen" })).toBeVisible();
  await expect(page.getByText("Coach status view")).toBeVisible();
  await expect(page.getByText("Modified participation")).toBeVisible();
  await expect(page.getByText("No contact drills. No full-speed cutting.")).toBeVisible();
  await expect(
    page.getByText("Awaiting named clinician decision. This shared view is not medical clearance."),
  ).toBeVisible();

  await expect(page.getByText("Symptom trend")).toHaveCount(0);
  await expect(page.getByText("Pain 5")).toHaveCount(0);
  await expect(page.getByText("guardian@example.com")).toHaveCount(0);
});
