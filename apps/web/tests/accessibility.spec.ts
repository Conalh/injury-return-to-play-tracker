import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const routes = [
  { name: "dashboard", path: "/" },
  { name: "case detail", path: "/cases/case_demo" },
  { name: "templates", path: "/templates" },
  { name: "coach share view", path: "/share/demo-coach-token" },
];

for (const route of routes) {
  test(`${route.name} has no serious automated accessibility violations`, async ({
    page,
  }) => {
    await page.goto(route.path);

    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();
    const blockingViolations = results.violations.filter((violation) =>
      ["serious", "critical"].includes(violation.impact ?? ""),
    );

    expect(
      blockingViolations.map((violation) => ({
        id: violation.id,
        impact: violation.impact,
        help: violation.help,
        targets: violation.nodes.map((node) => node.target),
      })),
    ).toEqual([]);
  });
}
