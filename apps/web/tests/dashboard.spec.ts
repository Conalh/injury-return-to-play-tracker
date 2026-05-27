import { expect, type Page, test } from "@playwright/test";

async function expectNoHorizontalOverflow(page: Page) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  expect(overflow).toBe(false);
}

test("clinician dashboard shows roster and evidence summary", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("navigation", { name: "Primary clinical navigation" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Stagewise dashboard" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Search athletes, cases, or evidence" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Return-to-Play Control Center" })).toBeVisible();
  await expect(page.getByText("Requires clinician review")).toBeVisible();
  await expect(page.getByText("Evidence overdue / due today")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Action queue" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Recent named decisions" })).toBeVisible();
  await expect(page.getByTestId("roster-table").getByRole("link", { name: /Riley Chen/ })).toBeVisible();
  await expect(page.getByRole("cell", { name: "Left ankle sprain" }).first()).toBeVisible();
  await expect(page.getByRole("columnheader", { name: "Missing gates" })).toBeVisible();
  await expect(page.getByTestId("roster-table").getByText("Review symptoms before advancing.")).toBeVisible();
});

test("case detail shows phase, milestones, evidence, readiness, and clearance panel", async ({ page }) => {
  await page.goto("/cases/case_demo");

  await expect(page.getByRole("heading", { name: "Riley Chen" })).toBeVisible();
  await expect(page.getByText("Held phase", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("Return-to-play phase progression")).toBeVisible();
  await expect(page.getByText("Restore motion")).toBeVisible();
  await expect(page.getByText("Pain remains below configured threshold", { exact: true })).toBeVisible();
  await expect(page.getByText("Symptom trend")).toBeVisible();
  await expect(page.getByText("Single leg hop")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Non-contact practice" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Readiness signals" })).toBeVisible();
  await expect(page.getByText("Stagewise does not auto-clear athletes")).toBeVisible();
  await expect(page.getByText("[object Object]")).toHaveCount(0);
  await expect(page.getByRole("link", { name: "Share access" }).first()).toBeVisible();
  await expect(page.getByText("Review symptoms before advancing.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Record clearance decision" })).toBeVisible();
});

test("dashboard stays inside the mobile viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Return-to-Play Control Center" })).toBeVisible();
  await expect(page.getByTestId("roster-table").getByRole("link", { name: /Riley Chen/ })).toBeVisible();
  await expectNoHorizontalOverflow(page);
});

test("case detail stays inside the mobile viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/cases/case_demo");

  await expect(page.getByRole("heading", { name: "Riley Chen" })).toBeVisible();
  await expect(page.getByText("Return-to-play phase progression")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Readiness signals" })).toBeVisible();
  await expectNoHorizontalOverflow(page);
});
