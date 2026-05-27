import { expect, test } from "@playwright/test";

test("clinician records evidence and readiness updates from case detail", async ({ page }) => {
  await page.goto("/cases/case_demo");

  await expect(page.getByRole("heading", { name: "Riley Chen" })).toBeVisible();

  await page.getByLabel("Symptom date").fill("2026-05-27");
  await page.getByLabel("Pain score").fill("8");
  await page.getByLabel("Swelling").selectOption("moderate");
  await page.getByLabel("Confidence").fill("2");
  await page.getByLabel("Symptom notes").fill("Pain increased after jogging.");
  await page.getByRole("button", { name: "Record symptoms" }).click();

  await expect(page.getByText("8/10")).toBeVisible();
  await expect(page.getByText("Review symptoms before advancing.")).toBeVisible();

  await page.getByLabel("Functional test name").fill("Balance reach");
  await page.getByLabel("Test date").fill("2026-05-27");
  await page.getByLabel("Result value").fill("82");
  await page.getByLabel("Result unit").fill("percent");
  await page.getByLabel("Side-to-side difference").fill("18");
  await page.getByLabel("Functional test outcome").selectOption("false");
  await page.getByLabel("Functional test notes").fill("Loss of control late in test.");
  await page.getByRole("button", { name: "Record functional test" }).click();

  await expect(page.getByText("Balance reach")).toBeVisible();
  await expect(page.getByRole("row", { name: /Balance reach/ })).toContainText("Review");

  await page.getByLabel("Workload date").fill("2026-05-27");
  await page.getByLabel("Activity").fill("Jog intervals");
  await page.getByLabel("Duration minutes").fill("12");
  await page.getByLabel("Intensity").fill("4");
  await page.getByLabel("Completed").selectOption("false");
  await page.getByLabel("Symptom response").fill("Pain increase during final interval.");
  await page.getByRole("button", { name: "Record workload" }).click();

  await expect(page.getByText("Jog intervals")).toBeVisible();
  await expect(page.getByText("Workload progression incomplete.")).toBeVisible();

  await page.getByLabel("Milestone status").selectOption("failed");
  await page.getByLabel("Milestone notes").fill("Evidence does not meet gate.");
  await page.getByLabel("Evidence source").fill("Browser evidence form");
  await page.getByRole("button", { name: "Attach milestone evidence" }).click();

  await expect(page.getByText("failed", { exact: true })).toBeVisible();
});
