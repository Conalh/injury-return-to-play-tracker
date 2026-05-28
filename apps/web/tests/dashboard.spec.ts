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

test("clinical controls expose polished hover and focus affordances", async ({ page }) => {
  await page.goto("/");

  const search = page.getByRole("button", { name: "Search athletes, cases, or evidence" });
  await search.hover();
  await expect(
    page.getByRole("tooltip", { name: "Search athletes, cases, or evidence across the clinical workspace" }),
  ).toBeVisible();
  await expect(search).toHaveCSS("transition-property", /background-color|box-shadow|transform|border-color|color/);

  const notifications = page.getByRole("button", { name: "Notifications" });
  await notifications.focus();
  await expect(page.getByRole("tooltip", { name: "Review clinical notifications" })).toBeVisible();

  await expect(page.locator(".rp-page")).toBeVisible();
  const pageWidthBeforeHover = await page.locator(".rp-page").evaluate((node) => node.getBoundingClientRect().width);
  await page.locator(".rp-kpi").first().hover();
  const pageWidthAfterHover = await page.locator(".rp-page").evaluate((node) => node.getBoundingClientRect().width);

  expect(pageWidthAfterHover).toBe(pageWidthBeforeHover);
  await expectNoHorizontalOverflow(page);
});

test("command search opens, filters, and routes to clinical work", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "Search athletes, cases, or evidence" }).click();
  await expect(page.getByRole("dialog", { name: "Clinical command search" })).toBeVisible();

  const searchbox = page.getByRole("searchbox", { name: "Search command palette" });
  await expect(searchbox).toBeFocused();
  await searchbox.fill("riley");
  await expect(page.getByRole("link", { name: /Riley Chen case detail/ })).toBeVisible();
  await page.getByRole("link", { name: /Riley Chen case detail/ }).click();

  await expect(page).toHaveURL(/\/cases\/case_demo$/);
  await expect(page.getByRole("heading", { name: "Riley Chen" })).toBeVisible();

  await page.keyboard.press("Control+K");
  await expect(page.getByRole("dialog", { name: "Clinical command search" })).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog", { name: "Clinical command search" })).toHaveCount(0);
});

test("notification center opens clinical alerts and routes to case work", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "Notifications" }).click();
  const notifications = page.getByRole("dialog", { name: "Clinical notifications" });
  await expect(notifications).toBeVisible();
  await expect(page.getByText("3 open clinical alerts")).toBeVisible();
  await expect(notifications.getByRole("link", { name: /Review symptoms before advancing/ })).toBeVisible();
  await expect(notifications.getByRole("link", { name: /Workload progression incomplete/ })).toBeVisible();

  await notifications.getByRole("link", { name: /Review symptoms before advancing/ }).click();
  await expect(page).toHaveURL(/\/cases\/case_demo#overview$/);
  await expect(page.getByRole("heading", { name: "Riley Chen" })).toBeVisible();

  await page.getByRole("button", { name: "Notifications" }).click();
  await expect(page.getByRole("dialog", { name: "Clinical notifications" })).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog", { name: "Clinical notifications" })).toHaveCount(0);
});

test("clinician profile menu opens workspace context and routes to tools", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "Physician workspace menu" }).click();
  const profileMenu = page.getByRole("dialog", { name: "Clinician workspace menu" });
  await expect(profileMenu).toBeVisible();
  await expect(profileMenu.getByText("Dr. Aanya Patel")).toBeVisible();
  await expect(profileMenu.getByText("Team Physician")).toBeVisible();
  await expect(profileMenu.getByText("Stagewise Athletic Medicine")).toBeVisible();
  await expect(profileMenu.getByText("Demo environment")).toBeVisible();
  await expect(profileMenu.getByRole("link", { name: /Open template management/ })).toBeVisible();
  await expect(profileMenu.getByRole("link", { name: /Open Riley Chen report/ })).toBeVisible();

  await profileMenu.getByRole("link", { name: /Open template management/ }).click();
  await expect(page).toHaveURL(/\/templates$/);
  await expect(page.getByRole("heading", { name: "Template builder" })).toBeVisible();

  await page.getByRole("button", { name: "Physician workspace menu" }).click();
  await expect(page.getByRole("dialog", { name: "Clinician workspace menu" })).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog", { name: "Clinician workspace menu" })).toHaveCount(0);
});

test("sidebar routes to dashboard workflow sections", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("navigation", { name: "Primary clinical navigation" }).getByRole("link", { name: /Active cases/ }).click();
  await expect(page).toHaveURL(/\/#active-cases$/);
  await expect(page.getByRole("region", { name: "Clinical workload summary" })).toBeVisible();

  await page.getByRole("navigation", { name: "Primary clinical navigation" }).getByRole("link", { name: /Athletes/ }).click();
  await expect(page).toHaveURL(/\/#athlete-roster$/);
  await expect(page.getByRole("region", { name: "Active athlete roster" })).toBeVisible();

  await page.getByRole("navigation", { name: "Primary clinical navigation" }).getByRole("link", { name: /Evidence queue/ }).click();
  await expect(page).toHaveURL(/\/#evidence-queue$/);
  await expect(page.getByRole("region", { name: "Evidence action queue" })).toBeVisible();

  await page.getByRole("navigation", { name: "Primary clinical navigation" }).getByRole("link", { name: /Decision queue/ }).click();
  await expect(page).toHaveURL(/\/#decision-queue$/);
  await expect(page.getByRole("region", { name: "Recent named decisions" })).toBeVisible();

  await page.getByRole("navigation", { name: "Primary clinical navigation" }).getByRole("link", { name: /Settings/ }).click();
  await expect(page).toHaveURL(/\/#workspace-settings$/);
  await expect(page.getByRole("region", { name: "Workspace settings" })).toBeVisible();

  await page.getByRole("button", { name: "Physician workspace menu" }).click();
  await page.getByRole("dialog", { name: "Clinician workspace menu" }).getByRole("link", { name: /Open workspace settings/ }).click();
  await expect(page).toHaveURL(/\/#workspace-settings$/);
  await expect(page.getByRole("region", { name: "Workspace settings" })).toBeVisible();
});

test("shell breadcrumbs and active navigation follow workspace context", async ({ page }) => {
  await page.goto("/");

  const nav = page.getByRole("navigation", { name: "Primary clinical navigation" });
  const breadcrumb = page.getByLabel("Workspace breadcrumb");

  await expect(breadcrumb).toHaveText("Clinical / Dashboard");
  await expect(nav.getByRole("link", { name: /^Dashboard$/ })).toHaveAttribute("aria-current", "page");

  await nav.getByRole("link", { name: /Evidence queue/ }).click();
  await expect(page).toHaveURL(/\/#evidence-queue$/);
  await expect(breadcrumb).toHaveText("Clinical / Evidence queue");
  await expect(nav.getByRole("link", { name: /Evidence queue/ })).toHaveAttribute("aria-current", "location");

  await page.goto("/templates");
  await expect(breadcrumb).toHaveText("Decisions & access / Templates");
  await expect(nav.getByRole("link", { name: /^Templates$/ })).toHaveAttribute("aria-current", "page");

  await page.goto("/cases/case_demo");
  await expect(breadcrumb).toHaveText("Clinical / Case detail");
  await expect(nav.getByRole("link", { name: /Active cases/ })).toHaveAttribute("aria-current", "page");

  await page.goto("/cases/new");
  await expect(breadcrumb).toHaveText("Clinical / New case");
  await expect(nav.getByRole("link", { name: /Active cases/ })).toHaveAttribute("aria-current", "page");
});

test("sidebar avoids decorative counts while dashboard metrics remain visible", async ({ page }) => {
  await page.goto("/");

  const nav = page.getByRole("navigation", { name: "Primary clinical navigation" });
  await expect(nav.locator(".rp-nav-count")).toHaveCount(0);
  await expect(page.getByRole("region", { name: "Clinical workload summary" })).toBeVisible();
  await expect(page.getByText("Across current clinical workspace")).toBeVisible();
  await expect(page.getByText("Cases with missing phase gates")).toBeVisible();
});
