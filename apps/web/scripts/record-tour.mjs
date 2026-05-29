// Records a ~28s product tour video of the Return-to-Play Control Center.
// Requires the dev server running in demo mode (npm run dev, port 3217).
// Usage: node scripts/record-tour.mjs
import { chromium } from "@playwright/test";
import { mkdirSync } from "node:fs";
import path from "node:path";

const BASE = process.env.TOUR_BASE_URL ?? "http://127.0.0.1:3217";
const OUT_DIR = path.resolve(process.cwd(), "output");
const SIZE = { width: 1440, height: 900 };

mkdirSync(OUT_DIR, { recursive: true });

function ease(t) {
  return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
}

async function smoothScrollTo(page, targetY, duration = 1600) {
  await page.evaluate(
    async ({ targetY, duration }) => {
      const easeFn = (t) => (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t);
      const startY = window.scrollY;
      const maxY = document.documentElement.scrollHeight - window.innerHeight;
      const dest = Math.min(targetY, Math.max(0, maxY));
      const delta = dest - startY;
      const start = performance.now();
      await new Promise((resolve) => {
        function step(now) {
          const t = Math.min(1, (now - start) / duration);
          window.scrollTo(0, startY + delta * easeFn(t));
          if (t < 1) requestAnimationFrame(step);
          else resolve();
        }
        requestAnimationFrame(step);
      });
    },
    { targetY, duration },
  );
}

async function moveTo(page, locator) {
  const box = await locator.boundingBox();
  if (!box) return;
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 28 });
}

async function main() {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: SIZE,
    deviceScaleFactor: 1,
    recordVideo: { dir: OUT_DIR, size: SIZE },
  });

  // Soft pointer that follows mouse moves so clicks read on camera.
  await context.addInitScript(() => {
    function mount() {
      if (document.getElementById("__tour_cursor")) return;
      const dot = document.createElement("div");
      dot.id = "__tour_cursor";
      Object.assign(dot.style, {
        position: "fixed",
        width: "22px",
        height: "22px",
        marginLeft: "-11px",
        marginTop: "-11px",
        borderRadius: "50%",
        background: "rgba(37,99,235,0.45)",
        border: "2px solid rgba(255,255,255,0.95)",
        boxShadow: "0 2px 8px rgba(15,23,42,0.45)",
        zIndex: "2147483647",
        pointerEvents: "none",
        left: "-100px",
        top: "-100px",
        transition: "left .09s ease-out, top .09s ease-out, transform .1s ease-out",
      });
      document.body.appendChild(dot);
      window.addEventListener(
        "mousemove",
        (e) => {
          dot.style.left = e.clientX + "px";
          dot.style.top = e.clientY + "px";
        },
        true,
      );
      window.addEventListener("mousedown", () => (dot.style.transform = "scale(0.7)"), true);
      window.addEventListener("mouseup", () => (dot.style.transform = "scale(1)"), true);
    }
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", mount);
    } else {
      mount();
    }
  });

  const page = await context.newPage();

  // --- Dashboard ---
  await page.goto(BASE, { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Return-to-Play Control Center" }).waitFor();
  await page.evaluate(() => document.fonts.ready);
  await page.mouse.move(SIZE.width / 2, 260, { steps: 20 });
  await page.waitForTimeout(2400);

  // Scroll to roster + action rail
  await smoothScrollTo(page, 360, 1700);
  await page.waitForTimeout(1500);
  await smoothScrollTo(page, 760, 1500);
  await page.waitForTimeout(1500);
  await smoothScrollTo(page, 0, 1200);
  await page.waitForTimeout(500);

  // --- Command palette ---
  const searchBtn = page.getByRole("button", { name: "Search athletes, cases, or evidence" });
  await moveTo(page, searchBtn);
  await searchBtn.click();
  await page.waitForTimeout(700);
  const searchInput = page.getByRole("searchbox", { name: "Search command palette" });
  await searchInput.pressSequentially("riley", { delay: 110 });
  await page.waitForTimeout(1900);
  await page.keyboard.press("Escape");
  await page.waitForTimeout(600);

  // Open the case from the roster row
  const rosterLink = page
    .getByTestId("roster-table")
    .getByRole("link", { name: /Riley Chen/ });
  await moveTo(page, rosterLink);
  await page.waitForTimeout(300);
  await rosterLink.click();

  // --- Case detail ---
  await page.getByRole("heading", { name: "Riley Chen" }).waitFor();
  await page.evaluate(() => document.fonts.ready);
  await page.mouse.move(SIZE.width / 2, 300, { steps: 18 });
  await page.waitForTimeout(2400);

  await smoothScrollTo(page, 420, 1600);
  await page.waitForTimeout(1500);
  await smoothScrollTo(page, 940, 1700);
  await page.waitForTimeout(1500);
  await smoothScrollTo(page, 1500, 1600);
  await page.waitForTimeout(1600);

  const video = page.video();
  await context.close();
  await browser.close();
  const out = await video.path();
  console.log("VIDEO:" + out);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
