"use strict";

const fs = require("fs");
const { expect } = require("@playwright/test");

const defaultBaseURL = fs.existsSync("/.dockerenv")
    ? "http://nginx:4000"
    : "http://boorudev:4000";
const baseURL = process.env.PLAYWRIGHT_BASE_URL || defaultBaseURL;
const username = process.env.E2E_USER || "admin";
const password = process.env.E2E_PASS || "admin1234";

async function login(page) {
    await page.goto(`${baseURL}/login`);
    await page.fill('input[name="name"]', username);
    await page.fill('input[name="password"]', password);
    await page.getByRole("button", { name: "Login" }).click();
    await page.waitForURL(`${baseURL}/`);
    await expect(page.locator("text=Logged in")).toBeVisible();
}

module.exports = {
    baseURL,
    login,
};
