"use strict";

const { test, expect } = require("@playwright/test");
const { login, baseURL } = require("./helpers");

test.describe("Autocomplete", () => {
    test("shows tag suggestions", async ({ page }) => {
        await login(page);
        await page.goto("/");
        const input = page.locator("#search-text");
        await input.fill("tag_00");

        await expect
            .poll(
                async () =>
                    page.locator(".autocomplete li").count(),
                { timeout: 5000 }
            )
            .toBeGreaterThan(0);
    });

    test("shows local suggestions while remote search is pending", async ({
        page,
    }) => {
        await login(page);

        const request = page.context().request;
        const allTagsRes = await request.get(
            `${baseURL}/api/all-tags?offset=0&limit=1&q=sort:usages&fields=names`
        );
        let allTags = await allTagsRes.json();
        if (!allTags.results || allTags.results.length === 0) {
            await request.post(`${baseURL}/api/tags`, {
                data: {
                    names: ["hybrid_local_tag"],
                    category: "general",
                },
            });
            const retryRes = await request.get(
                `${baseURL}/api/all-tags?offset=0&limit=1&q=sort:usages&fields=names`
            );
            allTags = await retryRes.json();
        }

        const tagName = allTags.results[0].names[0];
        const prefix = tagName.substring(0, Math.min(4, tagName.length));

        let releaseRemote;
        const remoteGate = new Promise((resolve) => {
            releaseRemote = resolve;
        });
        await page.route("**/api/tags?*", async (route) => {
            await remoteGate;
            await route.continue();
        });

        await page.goto("/");
        const input = page.locator("#search-text");
        await input.fill(prefix);

        await expect
            .poll(
                async () =>
                    page.locator(".autocomplete li").count(),
                { timeout: 1500 }
            )
            .toBeGreaterThan(0);

        releaseRemote();
    });
});
