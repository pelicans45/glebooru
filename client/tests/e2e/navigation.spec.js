"use strict";

const { test, expect } = require("@playwright/test");
const { login } = require("./helpers");

test.describe("Navigation", () => {
    test("navbar renders and links navigate", async ({ page }) => {
        await login(page);
        await page.goto("/");

        const nav = page.locator("#top-navigation");
        await expect(nav).toBeVisible();
        await expect(nav.getByRole("link", { name: "Gallery" })).toBeVisible();
        await expect(nav.getByRole("link", { name: "Upload" })).toBeVisible();
        await expect(nav.getByRole("link", { name: "Tags" })).toBeVisible();

        await nav.getByRole("link", { name: "Upload" }).click();
        await expect(page).toHaveURL(/\/upload/);

        await nav.getByRole("link", { name: "Tags" }).click();
        await expect(page).toHaveURL(/\/tags/);

        await nav.getByRole("link", { name: "Gallery" }).click();
        await expect(page).toHaveURL(/\/$/);

        const screenshot = await page.screenshot({ fullPage: true });
        test.info().attach("navigation-gallery", {
            body: screenshot,
            contentType: "image/png",
        });
    });
});
