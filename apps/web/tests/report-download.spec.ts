import { expect, test } from "@playwright/test";

test("case detail exposes a PDF report download", async ({ page }) => {
  await page.goto("/cases/case_demo");

  await expect(page.getByRole("heading", { name: "Riley Chen" })).toBeVisible();
  const downloadLink = page.getByRole("link", { name: "Download PDF report" });
  await expect(downloadLink).toBeVisible();
  await expect(downloadLink).toHaveAttribute("href", /\/cases\/case_.+\/report/);
});
