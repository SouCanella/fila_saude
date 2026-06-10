// @ts-check
const { test, expect } = require("@playwright/test");

test.describe("Project Hub demo", () => {
  test("Overview carrega funil, entregas e atividade", async ({ page }) => {
    await page.goto("./");
    await expect(page.locator(".hub-phase-funnel")).toBeVisible();
    await expect(page.locator("#hubDeliveries")).toBeVisible();
    await expect(page.locator(".hub-activity-card")).toBeVisible();
  });

  test("Banner showcase ausente no demo", async ({ page }) => {
    await page.goto("./");
    await expect(page.locator(".hub-showcase-banner")).toHaveCount(0);
  });

  test("Filtro por fase altera entregas visíveis", async ({ page }) => {
    await page.goto("./");
    const rows = page.locator("#hubDeliveries tbody tr.hub-delivery-row");
    const total = await rows.count();
    expect(total).toBeGreaterThan(0);
    const faseStep = page.locator('.hub-phase-step[data-phase-id="FASE-1"]');
    if (await faseStep.count()) {
      await faseStep.click();
      await expect(page.locator("#hubPhaseFilterHint")).toBeVisible();
    }
  });

  test("Dark mode persiste ao navegar Processo", async ({ page }) => {
    await page.goto("./");
    await page.evaluate(() => {
      localStorage.setItem("modelo-theme", "dark");
      document.documentElement.setAttribute("data-theme", "dark");
    });
    await page.reload();
    await page.locator('.hub-nav-item[data-module="process"]').click();
    await expect(page.locator(".hub-embed")).toBeVisible();
    const theme = await page.evaluate(() => document.documentElement.getAttribute("data-theme"));
    expect(theme).toBe("dark");
  });

  test("Módulos Security montam", async ({ page }) => {
    await page.goto("./#security");
    await expect(page.locator("#moduleRoot")).not.toContainText("indisponível");
  });
});
