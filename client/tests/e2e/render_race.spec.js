"use strict";

const { test, expect } = require("@playwright/test");
const { login } = require("./helpers");

const oneByOneGif =
    "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==";

function makeResponse(ids) {
    return {
        offset: 0,
        limit: 40,
        total: ids.length,
        hasMore: false,
        results: ids.map((id) => ({
            id,
            type: "image",
            safety: "safe",
            contentUrl: oneByOneGif,
            thumbnailUrl: oneByOneGif,
            score: 0,
            favoriteCount: 0,
            commentCount: 0,
            tagsBasic: [],
        })),
    };
}

test.describe("Gallery render race", () => {
    test("ignores stale responses after rapid safety toggles", async ({
        page,
    }) => {
        await login(page);

        let callCount = 0;
        await page.route("**/api/posts**", async (route) => {
            const requestUrl = new URL(route.request().url());
            if (
                requestUrl.pathname !== "/api/posts" &&
                requestUrl.pathname !== "/api/posts/"
            ) {
                await route.continue();
                return;
            }
            callCount += 1;
            const ids = callCount === 1 ? [1001, 1002] : [2001, 2002];
            if (callCount === 1) {
                await new Promise((resolve) => setTimeout(resolve, 1500));
            }
            await route.fulfill({
                status: 200,
                contentType: "application/json",
                body: JSON.stringify(makeResponse(ids)),
            });
        });

        await page.goto("/");
        await expect
            .poll(() => callCount, { timeout: 5000 })
            .toBeGreaterThanOrEqual(1);

        // Trigger a second request before the initial one returns.
        const searchInput = page.locator('form.search input[name="search-text"]');
        await searchInput.fill("race_test_tag");
        await searchInput.press("Enter");
        await expect(page).toHaveURL(/race_test_tag/);

        await expect
            .poll(() => callCount, { timeout: 5000 })
            .toBeGreaterThanOrEqual(2);
        await page.waitForTimeout(1600);

        const ids = await page
            .locator(".post-list li")
            .evaluateAll((els) =>
                els.map((el) => el.getAttribute("data-post-id"))
            );

        expect(ids.length).toBeGreaterThan(0);
        expect(ids.some((id) => id && id.startsWith("200"))).toBe(true);
        expect(ids.some((id) => id && id.startsWith("100"))).toBe(false);
    });
});
