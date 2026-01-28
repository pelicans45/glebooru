"use strict";

const { test, expect } = require("@playwright/test");
const { login } = require("./helpers");

test.describe("Gallery", () => {
    test("loads and infinite scrolls", async ({ page }) => {
        await login(page);
        await page.goto("/");
        const listLocator = page.locator(".post-list li");
        await expect
            .poll(async () => listLocator.count(), { timeout: 10000 })
            .toBeGreaterThan(0);

        const initialCount = await listLocator.count();
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await page.waitForTimeout(1000);
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

        await expect
            .poll(async () => listLocator.count(), {
                timeout: 10000,
            })
            .toBeGreaterThan(initialCount);
    });
});
