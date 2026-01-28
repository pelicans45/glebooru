"use strict";

const { test, expect } = require("@playwright/test");
const { login } = require("./helpers");

test.describe("Search", () => {
    test("navigates to tag search results", async ({ page }) => {
        await login(page);
        await page.goto("/");
        const input = page.locator("#search-text");
        await input.fill("tag_00000");
        await input.press("Enter");
        await page.waitForTimeout(500);
        await expect(page).toHaveURL(/tag_00000/);
        await expect(page.locator(".post-list li").first()).toBeVisible();
    });
});
