import { expect, test } from "@playwright/test";

test("audit history has its own case section the tab links to", async ({ page }) => {
  await page.goto("/cases/case_demo");

  const auditTab = page.getByRole("link", { name: "Audit history" });
  await expect(auditTab).toHaveAttribute("href", "#audit-history");

  await auditTab.click();
  await expect(
    page.getByRole("heading", { name: "Audit history" }),
  ).toBeVisible();
});

test("clinician can filter audit log to sensitive workflow reads", async ({ page }) => {
  await page.goto("/cases/case_demo");

  await expect(page.getByRole("heading", { name: "Riley Chen" })).toBeVisible();
  const downloadLink = page.getByRole("link", { name: "Download PDF report" });
  const reportHref = await downloadLink.getAttribute("href");
  expect(reportHref).toBeTruthy();
  await page.request.get(reportHref!);

  await page.reload();
  await expect(page.getByText("sensitive_export_read")).toBeVisible();

  await page.getByLabel("Audit event type").selectOption("sensitive_export_read");
  await expect(page.getByText("sensitive_export_read")).toBeVisible();
  await expect(page.getByText("share_created")).toHaveCount(0);
});
