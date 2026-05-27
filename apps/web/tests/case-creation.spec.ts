import { expect, test } from "@playwright/test";

test("clinician creates athlete, case, applies template, and lands on detail", async ({ page }) => {
  const athleteName = `Jordan Vale ${Date.now()}`;

  await page.goto("/cases/new");

  await expect(page.getByRole("heading", { name: "Create return-to-play case" })).toBeVisible();

  await page.getByLabel("Athlete name").fill(athleteName);
  await page.getByLabel("Date of birth").fill("2009-02-14");
  await page.getByLabel("Sport").fill("Basketball");
  await page.getByLabel("Position").fill("Guard");
  await page.getByLabel("Guardian email").fill("guardian@example.com");

  await page.getByLabel("Case title").fill("Right knee sprain");
  await page.getByLabel("Injury category").fill("sprain");
  await page.getByLabel("Body region").fill("knee");
  await page.getByLabel("Side").selectOption("right");
  await page.getByLabel("Date of injury").fill("2026-05-22");
  await page.getByLabel("Clinical summary").fill("Twisted knee during practice.");
  await expect(page.getByLabel("Return plan template").locator("option")).toContainText([
    "Select",
    /ankle return/i,
  ]);
  await page.getByLabel("Return plan template").selectOption({ index: 1 });

  await page.getByRole("button", { name: "Create case" }).click();

  await expect(page).toHaveURL(/\/cases\/case_/);
  await expect(page.getByTestId("case-detail")).toHaveAttribute("data-source", "api");
  await expect(page.getByRole("heading", { name: athleteName })).toBeVisible();
  await expect(page.getByText("Right knee sprain")).toBeVisible();
  await expect(page.getByText("Restore motion")).toBeVisible();
});

test("case creation surfaces required-field validation errors", async ({ page }) => {
  await page.goto("/cases/new");

  await page.getByRole("button", { name: "Create case" }).click();

  await expect(page.getByText("Please complete the required fields before creating the case.")).toBeVisible();
  await expect(page.getByText("Required", { exact: true })).toHaveCount(9);
});
