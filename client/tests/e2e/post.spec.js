"use strict";

const { test, expect } = require("@playwright/test");
const { login, createPost } = require("./helpers");

test.describe("Post view", () => {
    test("opens a post from the gallery", async ({ page }) => {
        await login(page);
        const tag = "e2e_post_view";
        const createdPost = await createPost(page, { tags: [tag], seed: 42 });

        await page.goto(`/?q=id:${createdPost.id}&limit=1`);
        const postLink = page.locator(
            `.post-list li[data-post-id="${createdPost.id}"] a`
        );
        await expect(postLink).toBeVisible();
        await postLink.click();
        await expect(page).toHaveURL(/\/\d+$/);
        await expect(page.locator(".post-view")).toBeVisible();
        await expect(page.locator(".download a")).toHaveCount(1);
        const tagDisplay = tag.replace(/_/g, " ");
        await expect(
            page.locator(".readonly-sidebar .compact-tags")
        ).toContainText(tagDisplay);

        const screenshot = await page.screenshot({ fullPage: true });
        test.info().attach("post-view", {
            body: screenshot,
            contentType: "image/png",
        });
    });
});
