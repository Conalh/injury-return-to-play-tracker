import { expect, test } from "@playwright/test";

test("dashboard and case detail render seeded FastAPI data", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByTestId("roster-table")).toHaveAttribute("data-source", "api");
  await expect(page.getByRole("link", { name: /Riley Chen/ })).toBeVisible();
  await expect(page.getByText("Left ankle sprain")).toBeVisible();

  await page.getByRole("link", { name: /Riley Chen/ }).click();

  await expect(page.getByTestId("case-detail")).toHaveAttribute("data-source", "api");
  await expect(page.getByRole("heading", { name: "Riley Chen" })).toBeVisible();
  await expect(page.getByText("Pain remains below configured threshold", { exact: true })).toBeVisible();
  await expect(page.getByText("Review symptoms before advancing.")).toBeVisible();
});
