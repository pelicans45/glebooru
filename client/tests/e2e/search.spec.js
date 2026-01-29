"use strict";

const { test, expect } = require("@playwright/test");
const { login, createPost } = require("./helpers");

test.describe("Search", () => {
    test("navigates to tag search results", async ({ page }) => {
        await login(page);
        const tag = `e2e_search_${Date.now()}`;
        const excludeTag = `${tag}_exclude`;
        const includePost = await createPost(page, { tags: [tag], seed: 1 });
        const excludePost = await createPost(page, {
            tags: [tag, excludeTag],
            seed: 2,
        });

        await page.goto("/");
        const input = page.locator("#search-text");
        await input.fill(`${tag} -${excludeTag}`);
        await input.press("Enter");
        await page.waitForTimeout(500);
        await expect(page).toHaveURL(new RegExp(tag));
        await expect(page.locator(".post-list li").first()).toBeVisible();

        const ids = await page
            .locator(".post-list li")
            .evaluateAll((els) =>
                els.map((el) => Number(el.getAttribute("data-post-id")))
            );
        expect(ids).toContain(includePost.id);
        expect(ids).not.toContain(excludePost.id);
    });
});
