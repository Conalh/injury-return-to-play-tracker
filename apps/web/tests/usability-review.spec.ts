import { expect, type Page, test } from "@playwright/test";

async function expectNoHorizontalOverflow(page: Page) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  expect(overflow).toBe(false);
}

test("keyboard users can skip directly to the clinical workspace", async ({ page }) => {
  await page.goto("/");

  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to clinical workspace" })).toBeFocused();

  await page.keyboard.press("Enter");
  await expect(page.locator("#clinical-workspace")).toBeFocused();
});

test("core clinician pages keep reviewed safety copy and mobile layout", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });

  await page.goto("/");
  await expect(page.getByText("Stagewise surfaces readiness signals and protocol completion.")).toBeVisible();
  await expect(page.getByText("It does not clear athletes.")).toBeVisible();
  await expectNoHorizontalOverflow(page);

  await page.goto("/cases/case_demo");
  await expect(page.getByText("Clinician review required before advancement.")).toBeVisible();
  await expect(page.getByText("this workflow never substitutes for a named clearance decision")).toBeVisible();
  await expect(page.getByRole("link", { name: "Share access" }).first()).toBeVisible();
  await expect(page.getByRole("button", { name: "Record clearance decision" })).toBeVisible();
  await expectNoHorizontalOverflow(page);
});
