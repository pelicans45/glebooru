"use strict";

const { test, expect } = require("@playwright/test");
const { login } = require("./helpers");

test.describe("Post view", () => {
    test("opens a post from the gallery", async ({ page }) => {
        await login(page);
        await page.goto("/");
        const firstThumb = page.locator(".post-list li a").first();
        await firstThumb.click();
        await expect(page).toHaveURL(/\/\d+$/);
        await expect(page.locator(".post-view")).toBeVisible();
        await expect(page.locator(".download a")).toHaveCount(1);
    });
});
