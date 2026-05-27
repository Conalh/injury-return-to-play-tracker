import { expect, test } from "@playwright/test";

test("clinician dashboard shows roster and evidence summary", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Return-to-play tracker" })).toBeVisible();
  await expect(page.getByRole("link", { name: /Riley Chen/ })).toBeVisible();
  await expect(page.getByText("Left ankle sprain")).toBeVisible();
  await expect(page.getByRole("columnheader", { name: "Missing gates" })).toBeVisible();
  await expect(page.getByText("Review symptoms before advancing.")).toBeVisible();
});

test("case detail shows phase, milestones, evidence, readiness, and clearance panel", async ({ page }) => {
  await page.goto("/cases/case_demo");

  await expect(page.getByRole("heading", { name: "Riley Chen" })).toBeVisible();
  await expect(page.getByText("Held phase", { exact: true })).toBeVisible();
  await expect(page.getByText("Restore motion")).toBeVisible();
  await expect(page.getByText("Pain remains below configured threshold", { exact: true })).toBeVisible();
  await expect(page.getByText("Symptom trend")).toBeVisible();
  await expect(page.getByText("Single leg hop")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Non-contact practice" })).toBeVisible();
  await expect(page.getByText("Review symptoms before advancing.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Record clearance decision" })).toBeVisible();
});
