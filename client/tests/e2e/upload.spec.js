"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const { test, expect } = require("@playwright/test");
const { login } = require("./helpers");

const PNG_BYTES = Buffer.from(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=",
    "base64"
);

function makeTempFile(name) {
    const filePath = path.join(os.tmpdir(), name);
    fs.writeFileSync(filePath, PNG_BYTES);
    return filePath;
}

test.describe.configure({ mode: "serial" });

test.describe("Upload", () => {
    test("uploads a new file", async ({ page }) => {
        await login(page);
        await page.goto("/upload");
        const filePath = makeTempFile(`upload-${Date.now()}.png`);
        await page.getByRole("button", { name: "Click, drop, or paste" }).click();
        await page.setInputFiles("input[type=file]", filePath);
        await page.getByRole("button", { name: "Upload" }).click();
        await expect(page.locator("text=Uploaded")).toBeVisible();
    });

    test("rejects duplicate uploads", async ({ page }) => {
        await login(page);
        await page.goto("/upload");
        const filePath = makeTempFile(`upload-dup-${Date.now()}.png`);
        await page.getByRole("button", { name: "Click, drop, or paste" }).click();
        await page.setInputFiles("input[type=file]", filePath);
        await page.getByRole("button", { name: "Upload" }).click();
        await expect(page.locator("text=Uploaded")).toBeVisible();

        await page.goto("/upload");
        await page.getByRole("button", { name: "Click, drop, or paste" }).click();
        await page.setInputFiles("input[type=file]", filePath);
        await page.getByRole("button", { name: "Upload" }).click();
        await expect(page.locator("text=File already uploaded")).toBeVisible();
    });
});
