"use strict";

const { test, expect } = require("@playwright/test");
const { login, ensurePostsWithTag } = require("./helpers");

test.describe("Gallery", () => {
    test("loads and infinite scrolls before the bottom", async ({ page }) => {
        await login(page);
        const tag = "e2e_scroll";
        await ensurePostsWithTag(page, tag, 30);

        await page.goto(`/?q=${encodeURIComponent(tag)}&limit=20`);
        const listLocator = page.locator(".post-list li");
        await expect
            .poll(async () => listLocator.count(), { timeout: 10000 })
            .toBeGreaterThan(0);

        const initialCount = await listLocator.count();
        const preloadPx = await page.evaluate(() =>
            Math.max(800, Math.round(window.innerHeight * 1.5))
        );
        await page.evaluate((margin) => {
            const maxScroll =
                document.body.scrollHeight - window.innerHeight;
            const target = Math.max(0, maxScroll - margin + 50);
            window.scrollTo(0, target);
        }, preloadPx);
        await page.waitForTimeout(500);

        await expect
            .poll(async () => listLocator.count(), {
                timeout: 10000,
            })
            .toBeGreaterThan(initialCount);

        const screenshot = await page.screenshot({ fullPage: true });
        test.info().attach("gallery-scroll", {
            body: screenshot,
            contentType: "image/png",
        });
    });
});
